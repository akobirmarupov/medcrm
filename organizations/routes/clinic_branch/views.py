from __future__ import annotations

from rest_framework.views import APIView
from rest_framework import status
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from organizations.models import Clinic, Branch
from common.permissions import IsAdmin, IsStaffWithAccountant
from organizations.routes.clinic_branch.serializers import (
                ClinicListSerializer, ClinicSerializer, BranchListSerializer, BranchSerializer)



class ClinicListCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsStaffWithAccountant()]
    
    def get(self, request):
        clinics = Clinic.objects.all().order_by('name')
        serializer = ClinicListSerializer(clinics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        serializer = ClinicSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ClinicDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == ('GET'):
            return [IsStaffWithAccountant()]
        return [IsAdmin()]
    
    def get_object(self, pk):
        try:
            return Clinic.objects.get(pk=pk)
        except Clinic.DoesNotExist:
            return None
        
    
    def get(self, request, pk):
        clinic = self.get_object(pk)

        if clinic is None:
            return Response({"detail": "Klinika topilmadi."},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClinicSerializer(clinic)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def put(self, request, pk):
        clinic = self.get_object(pk)
        if clinic is None:
            return Response(
                {'detail': 'Klinika topilmadi.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ClinicSerializer(clinic, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        clinic = self.get_object(pk)
        if clinic is None:
            return Response(
                {'detail': 'Klinika topilmadi.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if clinic.branches.exists():
            return Response(
                {'detail': 'Klinikaning filiallari mavjud. Avval filiallarni o\'chiring!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        clinic.delete()
        return Response(
            {'detail': 'Klinika muvaffaqiyatli o\'chirildi.'},
            status=status.HTTP_204_NO_CONTENT
        )
