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
    IsAdmin, IsDoctor, IsReceptionist, IsNurse, IsPatient,
    IsStaffWithAccountant, IsOwnerOrMedicalStaff, IsMedicalStaff
)
from patients.routes.allergy_chronic.serializers import (
    PatientAllergyReadSerializer, PatientAllergyWriteSerializer,
    PatientChronicDiseaseReadSerializer, PatientChronicDiseaseWriteSerializer)
from patients.models import PatientAllergy, PatientChronicDisease
from common.pagination import StandardPagination


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
        serializer = PatientAllergyWriteSerializer(data=request.data)

        if serializer.is_valid():
            allergy = serializer.save()
            logger.info(f"[CREATE] PatientAllergy '{allergy.allergen}' (patient_id={allergy.patient_id}) — user: {request.user}")
            return Response(PatientAllergyReadSerializer(allergy).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        


class PatientAllergyDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    qeryset = PatientAllergy.objects.none()
    owner_field = 'user'

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