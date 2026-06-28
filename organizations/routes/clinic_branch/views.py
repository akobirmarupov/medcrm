from __future__ import annotations

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from organizations.filters import ClinicFilter, BranchFilter
from drf_spectacular.utils import extend_schema

from django.core.cache import cache
import logging

from common.permissions import IsAdmin, IsStaffWithAccountant
from organizations.routes.clinic_branch.serializers import (
                ClinicListSerializer, ClinicSerializer, BranchListSerializer, BranchSerializer)
from organizations.models import Clinic, Branch
from common.pagination import StandardPagination



logger = logging.getLogger('organizations')



class ClinicListCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClinicFilter
    search_fields = ['name', 'legal_name', 'phone']
    ordering_fields = ['name', 'created_at']


    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsStaffWithAccountant()]
    
    
    @extend_schema(summary="Barcha klinikalar", responses={200: ClinicSerializer(many=True)}, tags=["Clinics"])
    def get(self, request):
        cache_key = f"clinics_list_{request.query_params.urlencode()}"
        data = cache.get(cache_key)

        if data is None:
            clinics = Clinic.objects.prefetch_related('branches').all().order_by('name')


            for backend in self.filter_backends:
                clinics = backend().filter_queryset(request, clinics, self)

            
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(clinics, request)
            serializer = ClinicListSerializer(page, many=True)

            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=60 * 5)

        return Response(data, status=status.HTTP_200_OK)
        

    @extend_schema(summary="Yangi klinika yaratish", request=ClinicSerializer, responses={201: ClinicSerializer}, tags=["Clinics"])
    def post(self, request):
        serializer = ClinicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("clinics_list_*")
            logger.info(f"[CREATE] Clinic '{serializer.data['name']}' — user: {request.user}")
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
        
    
    @extend_schema(summary="Klinika ma'lumotlari", responses={200: ClinicSerializer}, tags=["Clinics"])
    def get(self, request, pk):
        clinic = self.get_object(pk)

        if clinic is None:
            return Response({"detail": "Klinika topilmadi."},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClinicSerializer(clinic)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @extend_schema(summary="Klinikani yangilash", request=ClinicSerializer, responses={200: ClinicSerializer}, tags=["Clinics"])
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
            cache.delete_pattern("clinics_list_*")
            logger.info(f"[UPDATE] Clinic '{clinic.name}' (id={pk}) — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(summary="Klinikani o'chirish", responses={204: None}, tags=["Clinics"])
    def delete(self, request, pk):
        clinic = self.get_object(pk)
        if clinic is None:
            return Response({'detail': 'Klinika topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if clinic.branches.exists():
            return Response(
                {'detail': 'Klinikaning filiallari mavjud. Avval filiallarni o\'chiring!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"[DELETE] Clinic '{clinic.name}' (id={pk}) — user: {request.user}")
        clinic.delete()
        cache.delete_pattern("clinics_list_*")
        return Response({'detail': 'Klinika muvaffaqiyatli o\'chirildi.'}, status=status.HTTP_204_NO_CONTENT)


"""----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----"""


class BranchListCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BranchFilter
    search_fields = ['clinic__name', 'name', 'phone']
    ordering_fields = ['name', 'created_at']

    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsStaffWithAccountant()]
    

    @extend_schema(summary="Barcha Filiallar klinikalari", responses={200: BranchListSerializer(many=True)}, tags=["Branch"])
    def get(self, request):
        cache_key = f"branch_list_{request.query_params.urlencode()}"
        data = cache.get(cache_key)

        if data is None:
            branch = Branch.objects.select_related('clinic').all().order_by('name')

            for backend in self.filter_backends:
                branch = backend().filter_queryset(request, branch, self)

            
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(branch, request)
            serializer = BranchListSerializer(page, many=True)

            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=60 * 5)

        return Response(data, status=status.HTTP_200_OK)

    

    @extend_schema(summary="Yangi filial klinikasi yaratish", request=BranchSerializer, responses={201: BranchSerializer}, tags=["Branch"])
    def post(self, request):
        serializer = BranchSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("branch_list_*")
            logger.info(f"[CREATE] Branch '{serializer.data['name']}' — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    

class BranchDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsStaffWithAccountant()]
        return [IsAdmin()]
    

    def get_object(self, pk):
        try:
            return Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return None
        
    
    @extend_schema(summary="Klinika ma'lumotlari", responses={200: BranchSerializer}, tags=["Branch"])
    def get(self, request, pk):
        branch = self.get_object(pk)

        if branch is None:
            return Response({"detail": "Clinika filiali topilmadi."},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = BranchSerializer(branch)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @extend_schema(summary="Filialni yangilash", request=BranchSerializer, responses={200: BranchSerializer}, tags=["Branch"])
    def put(self, request, pk):
        branch = self.get_object(pk)

        if branch is None:
            return Response({"detail": "Clinika filiali  topilmadi."},
                             status=status.HTTP_404_NOT_FOUND)
        
        serializer = BranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("branch_list_*")
            logger.info(f"[UPDATE] Branch '{branch.name}' (id={pk}) — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    @extend_schema(summary="Filialni o'chirish", responses={204: None}, tags=["Branch"])
    def delete(self, request, pk):
        branch = self.get_object(pk)

        if branch is None:
            return Response({"detail": "Clinika filiali topilmadi."},
                             status=status.HTTP_404_NOT_FOUND)
        
        logger.info(f"[DELETE] Branch '{branch.name}' (id={pk}) — user: {request.user}")
        branch.delete()
        cache.delete_pattern("branch_list_*")
        return Response({"detail": "Clinika filiali muvaffaqiyatli o'chirildi."},
                        status=status.HTTP_204_NO_CONTENT)