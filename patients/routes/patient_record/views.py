from __future__ import annotations

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from patients.filters import PatientFilter, MedicalRecordFilter
from drf_spectacular.utils import extend_schema

from django.core.cache import cache
import logging

from common.permissions import (
    IsAdmin, IsDoctor, IsReceptionist, IsNurse, IsPatient,
    IsStaffWithAccountant, IsOwnerOrMedicalStaff,
)
from patients.routes.patient_record.serializers import (
    PatientSerializer, PatientListSerializer,
    MedicalRecordSerializer, MedicalRecordListSerializer)
from patients.models import Patient, MedicalRecord
from common.pagination import StandardPagination


logger = logging.getLogger('patients')


class PatientListCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PatientFilter
    search_fields = ['user__first_name', 'user__last_name', 'user__phone_number', 'pinfl', 'emergency_contact_name']
    ordering_fields = ['pinfl', 'created_at']
    queryset = Patient.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [(IsAdmin | IsReceptionist)()]
        return [(IsAdmin | IsReceptionist | IsDoctor)()]

    def get_queryset(self, request):
        qs = Patient.objects.select_related('user', 'user__profile').all()

        if getattr(request.user, 'role', None) == 'DOCTOR':
            qs = qs.filter(medical_records__doctor=request.user).distinct()

        return qs.order_by('-created_at')

    @extend_schema(summary="Barcha bemorlar", responses={200: PatientListSerializer(many=True)}, tags=["Patients"])
    def get(self, request):
        cache_key = f"patients_list_{request.user.role}_{request.user.id}_{request.query_params.urlencode()}"
        data = cache.get(cache_key)

        if data is None:
            patients = self.get_queryset(request)

            for backend in self.filter_backends:
                patients = backend().filter_queryset(request, patients, self)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(patients, request)
            serializer = PatientListSerializer(page, many=True)

            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=60 * 5)

        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(summary="Yangi bemor yaratish", request=PatientSerializer, responses={201: PatientSerializer}, tags=["Patients"])
    def post(self, request):
        serializer = PatientSerializer(data=request.data)

        if serializer.is_valid():
            patient = serializer.save()
            cache.delete_pattern("patients_list_*")
            logger.info(f"[CREATE] Patient '{patient.full_name}' (pinfl={patient.pinfl}) — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PatientDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Patient.objects.none()
    owner_field = 'user'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsStaffWithAccountant | IsOwnerOrMedicalStaff)()]
        if self.request.method == 'PUT':
            return [(IsAdmin | IsReceptionist | IsDoctor)()]
        return [IsAdmin()]

    def get_object(self, pk):
        try:
            return Patient.objects.select_related('user', 'user__profile').get(pk=pk)
        except Patient.DoesNotExist:
            return None

    def check_doctor_access(self, request, patient) -> bool:
        if getattr(request.user, 'role', None) != 'DOCTOR':
            return True
        return patient.medical_records.filter(doctor=request.user).exists()

    @extend_schema(summary="Bemor profili", responses={200: PatientSerializer}, tags=["Patients"])
    def get(self, request, pk):
        patient = self.get_object(pk)

        if patient is None:
            return Response({"detail": "Bunday id da bemor topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if getattr(request.user, 'role', None) == 'PATIENT' and patient.user_id != request.user.id:
            return Response({"detail": "Faqat o'z profilingizni ko'rishingiz mumkin."},
                             status=status.HTTP_403_FORBIDDEN)

        if not self.check_doctor_access(request, patient):
            return Response({"detail": "Ushbu bemor sizga biriktirilmagan."},
                             status=status.HTTP_403_FORBIDDEN)

        serializer = PatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(summary="Bemor ma'lumotlarini yangilash", request=PatientSerializer, responses={200: PatientSerializer}, tags=["Patients"])
    def put(self, request, pk):
        patient = self.get_object(pk)

        if patient is None:
            return Response({"detail": "Bemor topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("patients_list_*")
            logger.info(f"[UPDATE] Patient (id={pk}) — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(summary="Bemorni o'chirish", responses={204: None}, tags=["Patients"])
    def delete(self, request, pk):
        patient = self.get_object(pk)

        if patient is None:
            return Response({"detail": "Bemor topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if patient.medical_records.exists():
            return Response(
                {"detail": "Bemorning tibbiy yozuvlari mavjud. Avval ularni o'chiring!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"[DELETE] Patient (id={pk}) — user: {request.user}")
        patient.delete()
        cache.delete_pattern("patients_list_*")
        return Response({"detail": "Bemor muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)


"""----####----####----####----####----####----####----####----####----####----####----"""


class MedicalRecordListCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MedicalRecordFilter
    search_fields = ['title', 'patient__pinfl', 'patient__user__first_name', 'patient__user__last_name']
    ordering_fields = ['created_at']
    queryset = MedicalRecord.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [(IsDoctor | IsAdmin)()]
        return [(IsAdmin | IsDoctor | IsPatient)()]

    def get_queryset(self, request):
        qs = MedicalRecord.objects.select_related(
            'patient__user', 'patient__user__profile', 'doctor'
        ).all()

        role = getattr(request.user, 'role', None)
        if role == 'DOCTOR':
            qs = qs.filter(doctor=request.user)
        elif role == 'PATIENT':
            qs = qs.filter(patient__user=request.user)

        return qs.order_by('-created_at')

    @extend_schema(summary="Tibbiy yozuvlar ro'yxati", responses={200: MedicalRecordListSerializer(many=True)}, tags=["MedicalRecords"])
    def get(self, request):
        cache_key = f"medical_records_{request.user.role}_{request.user.id}_{request.query_params.urlencode()}"
        data = cache.get(cache_key)

        if data is None:
            records = self.get_queryset(request)

            for backend in self.filter_backends:
                records = backend().filter_queryset(request, records, self)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(records, request)
            serializer = MedicalRecordListSerializer(page, many=True)

            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=60 * 5)

        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(summary="Yangi tibbiy yozuv yaratish", request=MedicalRecordSerializer, responses={201: MedicalRecordSerializer}, tags=["MedicalRecords"])
    def post(self, request):
        serializer = MedicalRecordSerializer(data=request.data)

        if serializer.is_valid():
            record = serializer.save(doctor=request.user)
            cache.delete_pattern("medical_records_*")
            logger.info(f"[CREATE] MedicalRecord '{record.title}' for patient_id={record.patient_id} — doctor: {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedicalRecordDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = MedicalRecord.objects.none()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [(IsAdmin | IsDoctor | IsPatient)()]
        return [(IsAdmin | IsDoctor)()]

    def get_object(self, pk):
        try:
            return MedicalRecord.objects.select_related(
                'patient__user', 'patient__user__profile', 'doctor'
            ).get(pk=pk)
        except MedicalRecord.DoesNotExist:
            return None

    def has_object_access(self, request, record) -> bool:
        role = getattr(request.user, 'role', None)
        if request.user.is_superuser or role == 'ADMIN':
            return True
        if role == 'DOCTOR':
            return record.doctor_id == request.user.id
        if role == 'PATIENT':
            return record.patient.user_id == request.user.id
        return False

    @extend_schema(summary="Tibbiy yozuv tafsiloti", responses={200: MedicalRecordSerializer}, tags=["MedicalRecords"])
    def get(self, request, pk):
        record = self.get_object(pk)

        if record is None:
            return Response({"detail": "Tibbiy yozuv topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if not self.has_object_access(request, record):
            return Response({"detail": "Ushbu yozuvga ruxsatingiz yo'q."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(summary="Tibbiy yozuvni yangilash", request=MedicalRecordSerializer, responses={200: MedicalRecordSerializer}, tags=["MedicalRecords"])
    def put(self, request, pk):
        record = self.get_object(pk)

        if record is None:
            return Response({"detail": "Tibbiy yozuv topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        role = getattr(request.user, 'role', None)
        if role == 'DOCTOR' and record.doctor_id != request.user.id:
            return Response({"detail": "Faqat o'zingiz yozgan yozuvni tahrirlay olasiz."},
                             status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalRecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("medical_records_*")
            logger.info(f"[UPDATE] MedicalRecord (id={pk}) — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Tibbiy yozuvni o'chirish", responses={204: None}, tags=["MedicalRecords"])
    def delete(self, request, pk):
        record = self.get_object(pk)

        if record is None:
            return Response({"detail": "Tibbiy yozuv topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"[DELETE] MedicalRecord (id={pk}, patient_id={record.patient_id}) — user: {request.user}")
        record.delete()
        cache.delete_pattern("medical_records_*")
        return Response({"detail": "Tibbiy yozuv muvaffaqiyatli o'chirildi."}, status=status.HTTP_204_NO_CONTENT)