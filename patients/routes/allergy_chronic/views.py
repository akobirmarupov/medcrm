from __future__ import annotations

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from patients.filters import PatientAllergyFilter, PatientChronicDiseaseFilter
from drf_spectacular.utils import extend_schema

import logging

from common.permissions import (
    IsAdmin, IsDoctor, IsNurse, IsPatient, IsMedicalStaff)
from patients.routes.allergy_chronic.serializers import (
    PatientAllergyReadSerializer, PatientAllergyWriteSerializer,
    PatientChronicDiseaseReadSerializer, PatientChronicDiseaseWriteSerializer)
from patients.models import PatientAllergy, PatientChronicDisease
from common.pagination import StandardPagination
from patients.models import Patient


logger = logging.getLogger('patients')


class PatientAllergyListCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PatientAllergyFilter
    search_fields = ['allergen', 'patient__user__first_name', 'patient__user__last_name', 'patient__pinfl']
    ordering_fields = ['created_at', 'severity']
    queryset = PatientAllergy.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [(IsAdmin | IsDoctor)()]
        return [(IsAdmin | IsDoctor | IsNurse | IsPatient)()]

    def get_queryset(self, request):
        qs = PatientAllergy.objects.select_related('patient__user', 'patient__user__profile')

        role = getattr(request.user, 'role', None)
        if role == 'DOCTOR':
            qs = qs.filter(patient__medical_records__doctor=request.user).distinct()
        elif role == 'PATIENT':
            qs = qs.filter(patient__user=request.user)

        return qs.order_by('-created_at')


    def _doctor_can_access_patient(self, request, patient_id) -> bool:
        role = getattr(request.user, 'role', None)
        if role != 'DOCTOR':
            return True
        return Patient.objects.filter(
            pk=patient_id, medical_records__doctor=request.user
        ).exists()

    @extend_schema(summary="Barcha allergiyalar", responses={200: PatientAllergyReadSerializer(many=True)}, tags=["Allergy"])
    def get(self, request):
        allergy = self.get_queryset(request)

        for backend in self.filter_backends:
            allergy = backend().filter_queryset(request, allergy, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(allergy, request)
        serializer = PatientAllergyReadSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(summary="Yangi allergiya yaratish", request=PatientAllergyWriteSerializer,
                    responses={201: PatientAllergyReadSerializer}, tags=["Allergy"])
    def post(self, request):
        # FIX: eng jiddiy xato shu yerda edi — doctor istalgan patient_id yuborib,
        # o'ziga aloqasi bo'lmagan bemorga yozuv yaratishi mumkin edi.
        # Endi doctor faqat o'z bemoriga yozuv qo'sha oladi.
        patient_id = request.data.get('patient')
        if patient_id and not self._doctor_can_access_patient(request, patient_id):
            return Response(
                {"detail": "Siz faqat o'zingizga biriktirilgan bemorlarga yozuv qo'sha olasiz."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PatientAllergyWriteSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            allergy = serializer.save()
            logger.info(f"[CREATE] PatientAllergy '{allergy.allergen}' (patient_id={allergy.patient_id}) — user: {request.user}")
            return Response(PatientAllergyReadSerializer(allergy).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientAllergyDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = PatientAllergy.objects.none()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsMedicalStaff | IsPatient)()]
        return [(IsAdmin | IsDoctor)()]

    def get_object(self, pk):
        try:
            return PatientAllergy.objects.select_related(
                'patient__user', 'patient__user__profile'
            ).get(pk=pk)
        except PatientAllergy.DoesNotExist:
            return None

    def check_access(self, request, allergy) -> bool:
        role = getattr(request.user, 'role', None)
        if role == 'DOCTOR':
            return allergy.patient.medical_records.filter(doctor=request.user).exists()
        if role == 'PATIENT':
            return allergy.patient.user_id == request.user.id
        return True

    @extend_schema(summary="Allergiya tafsiloti", responses={200: PatientAllergyReadSerializer}, tags=["Allergy"])
    def get(self, request, pk):
        allergy = self.get_object(pk)

        if allergy is None:
            return Response({"detail": "Allergiya topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if not self.check_access(request, allergy):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PatientAllergyReadSerializer(allergy)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Bemor Alergiya va dakumentini yangilash", request=PatientAllergyWriteSerializer, responses={200: PatientAllergyWriteSerializer}, tags=["Allergy"])
    def put(self, request, pk):
        allergy = self.get_object(pk)

        if allergy is None:
            return Response({"detail": "Bunday ID da allergiyasi bor bemor topilmadi."},
                             status=status.HTTP_404_NOT_FOUND)

        if not self.check_access(request, allergy):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data.pop('patient', None)

        serializer = PatientAllergyWriteSerializer(allergy, data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[UPDATE] Patient Allergy (id={pk}) - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Allergiyani qisman yangilash", request=PatientAllergyWriteSerializer,
                    responses={200: PatientAllergyReadSerializer}, tags=["Allergy"])
    def patch(self, request, pk):
        allergy = self.get_object(pk)

        if allergy is None:
            return Response({"detail": "Bunday ID da allergiya topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if not self.check_access(request, allergy):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data.pop('patient', None)

        serializer = PatientAllergyWriteSerializer(allergy, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[PATCH] Patient Allergy (id={pk}) - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(summary="Bemorni Allergiya xatini o'chirish", responses={204: None}, tags=["Allergy"])
    def delete(self, request, pk):
        allergy = self.get_object(pk)

        if allergy is None:
            # FIX: bo'sh "..." xabar edi -> aniq matn qo'yildi (boshqa 404 javoblari bilan izchil)
            return Response({"detail": "Bunday ID da allergiya topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if not self.check_access(request, allergy):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        logger.info(f"[DELETE] Patient Allergy (id={pk}) — user: {request.user}")
        allergy.delete()
        return Response({"detail": "Allergiya yozuvi muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)


"""----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####"""


class PatientChronicDiseaseListCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PatientChronicDiseaseFilter
    search_fields = ['disease_name', 'icd_code', 'patient__user__first_name', 'patient__user__last_name', 'patient__pinfl']
    ordering_fields = ['created_at', 'diagnosed_at', 'is_active']
    queryset = PatientChronicDisease.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [(IsAdmin | IsDoctor)()]
        return [(IsAdmin | IsDoctor | IsNurse | IsPatient)()]

    def get_queryset(self, request):
        qs = PatientChronicDisease.objects.select_related('patient__user', 'patient__user__profile')

        role = getattr(request.user, 'role', None)
        if role == 'DOCTOR':
            qs = qs.filter(patient__medical_records__doctor=request.user).distinct()
        elif role == 'PATIENT':
            qs = qs.filter(patient__user=request.user)

        return qs.order_by('-created_at')


    def _doctor_can_access_patient(self, request, patient_id) -> bool:
        role = getattr(request.user, 'role', None)
        if role != 'DOCTOR':
            return True
        from patients.models import Patient
        return Patient.objects.filter(
            pk=patient_id, medical_records__doctor=request.user
        ).exists()

    @extend_schema(summary="Barcha surunkali kasalliklar", responses={200: PatientChronicDiseaseReadSerializer(many=True)}, tags=["ChronicDisease"])
    def get(self, request):
        diseases = self.get_queryset(request)

        for backend in self.filter_backends:
            diseases = backend().filter_queryset(request, diseases, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(diseases, request)
        serializer = PatientChronicDiseaseReadSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(summary="Yangi surunkali kasallik yaratish", request=PatientChronicDiseaseWriteSerializer,
                    responses={201: PatientChronicDiseaseReadSerializer}, tags=["ChronicDisease"])
    def post(self, request):
        # FIX: allergiyadagi bilan bir xil xato — doctor-patient bog'liqligi tekshirilmagan edi.
        patient_id = request.data.get('patient')
        if patient_id and not self._doctor_can_access_patient(request, patient_id):
            return Response(
                {"detail": "Siz faqat o'zingizga biriktirilgan bemorlarga yozuv qo'sha olasiz."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PatientChronicDiseaseWriteSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            disease = serializer.save()
            logger.info(f"[CREATE] PatientChronicDisease '{disease.disease_name}' (patient_id={disease.patient_id}) — user: {request.user}")
            return Response(PatientChronicDiseaseReadSerializer(disease).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientChronicDiseaseDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = PatientChronicDisease.objects.none()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsMedicalStaff | IsPatient)()]
        return [(IsAdmin | IsDoctor)()]

    def get_object(self, pk):
        try:
            return PatientChronicDisease.objects.select_related(
                'patient__user', 'patient__user__profile'
            ).get(pk=pk)
        except PatientChronicDisease.DoesNotExist:
            return None

    def check_access(self, request, disease) -> bool:
        role = getattr(request.user, 'role', None)
        if role == 'DOCTOR':
            return disease.patient.medical_records.filter(doctor=request.user).exists()
        if role == 'PATIENT':
            return disease.patient.user_id == request.user.id
        return True

    @extend_schema(summary="Surunkali kasallik tafsiloti", responses={200: PatientChronicDiseaseReadSerializer}, tags=["ChronicDisease"])
    def get(self, request, pk):
        disease = self.get_object(pk)

        if disease is None:
            return Response({"detail": "Surunkali kasallik topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if not self.check_access(request, disease):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        serializer = PatientChronicDiseaseReadSerializer(disease)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Surunkali kasallikni to'liq yangilash", request=PatientChronicDiseaseWriteSerializer,
                    responses={200: PatientChronicDiseaseReadSerializer}, tags=["ChronicDisease"])
    def put(self, request, pk):
        disease = self.get_object(pk)

        if disease is None:
            return Response({"detail": "Bunday ID da surunkali kasallik topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if not self.check_access(request, disease):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        # FIX: patient maydonini o'zgartirishga yo'l qo'yilmaydi (yuqoridagi izohga qarang).
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data.pop('patient', None)

        serializer = PatientChronicDiseaseWriteSerializer(disease, data=data, partial=False, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[UPDATE] PatientChronicDisease (id={pk}) - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Surunkali kasallikni qisman yangilash", request=PatientChronicDiseaseWriteSerializer,
                    responses={200: PatientChronicDiseaseReadSerializer}, tags=["ChronicDisease"])
    def patch(self, request, pk):
        disease = self.get_object(pk)

        if disease is None:
            return Response({"detail": "Bunday ID da surunkali kasallik topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if not self.check_access(request, disease):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        data.pop('patient', None)

        serializer = PatientChronicDiseaseWriteSerializer(disease, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"[PATCH] PatientChronicDisease (id={pk}) - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Surunkali kasallikni o'chirish", responses={204: None}, tags=["ChronicDisease"])
    def delete(self, request, pk):
        disease = self.get_object(pk)

        if disease is None:
            return Response({"detail": "Bunday ID da surunkali kasallik topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if not self.check_access(request, disease):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        logger.info(f"[DELETE] PatientChronicDisease (id={pk}) — user: {request.user}")
        disease.delete()
        return Response({"detail": "Surunkali kasallik yozuvi muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)