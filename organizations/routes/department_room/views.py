from __future__ import annotations

from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend
from organizations.filters import DepartmentFilter, RoomFilter
from drf_spectacular.utils import extend_schema

from django.core.cache import cache
import logging

from common.permissions import IsAdmin, IsStaffWithAccountant
from organizations.routes.department_room.serializers import (
    DepartmentListSerializer, DepartmentSerializer,
    RoomListSerializer, RoomSerializer)
from organizations.models import Department, Room
from common.pagination import StandardPagination


logger = logging.getLogger('organizations')


class DepartmentCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'head_doctor__first_name', 'head_doctor__last_name']
    ordering_fields = ['name', 'created_at']
    filterset_class = DepartmentFilter
    queryset = Department.objects.none()


    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsStaffWithAccountant()]
    

    @extend_schema(summary="Barcha bo'limlar", responses={200: DepartmentListSerializer(many=True)}, tags=["Deportament"])
    def get(self, request):
        cache_key = f"department_list_{request.query_params.urlencode()}"
        data = cache.get(cache_key)

        if data is None:
            deportament = Department.objects.select_related('branch', 'head_doctor').filter(is_active=True).order_by('name')

            for backend in self.filter_backends:
                deportament = backend().filter_queryset(request, deportament, self)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(deportament, request)
            serializer = DepartmentListSerializer(page, many=True)

            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout= 60 * 4)

        return Response(data, status=status.HTTP_200_OK)
        


    @extend_schema(summary="Yangi bo'lim yaratish", request=DepartmentSerializer, responses={201: DepartmentSerializer}, tags=["Deportament"])
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("department_list_*")
            logger.info(f"[CREATE] Deportament '{serializer.data['name']}, - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class DepartmentDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Department.objects.none()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsStaffWithAccountant()]
        return [IsAdmin()]
    

    def get_object(self, pk):
        try:
            return Department.objects.select_related('branch', 'head_doctor').get(pk=pk, is_active=True)
        except Department.DoesNotExist:
            return None
            

    
    @extend_schema(summary="Bo'lim ma'lumotlari", responses={200: DepartmentSerializer}, tags=["Deportament"])
    def get(self, request, pk):
        departament = self.get_object(pk)

        if departament is None:
            return Response({"detail": "Bo'lim topilmadi."},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = DepartmentSerializer(departament)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    @extend_schema(summary="Bo'lim yangilash", request=DepartmentSerializer, responses={200: DepartmentSerializer}, tags=["Deportament"])
    def put(self, request, pk):
        departament = self.get_object(pk)

        if departament is None:
            return Response({"detail": "O'zgartirish uchun bo'lim topilmadi."},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = DepartmentSerializer(departament, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("department_list_*")
            logger.info(f"[UPDATE] Departament '{departament.name}' (id={pk}) — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(summary="Bo'lim o'chirish", responses={200: None}, tags=["Deportament"])
    def delete(self, request, pk):
        departament = self.get_object(pk)

        if departament is None:
            return Response({"detail": "O'chirish uchun bo'lim topilmadi."},
                            status=status.HTTP_404_NOT_FOUND)
        
        departament.is_active = False
        departament.save(update_fields=['is_active'])

        departament.rooms.filter(is_active=True).update(is_active=False)

        cache.delete_pattern("department_list_*")
        logger.info(f"[SOFT DELETE] Department '{departament.name}' (id={pk}) — user: {request.user}")
        return Response({'detail': "Bo'lim muvaffaqiyatli yopildi."}, status=status.HTTP_200_OK)



"""----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----####----"""


class RoomCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoomFilter
    search_fields = ['number', 'name', 'room_type']
    ordering_fields = ['name', 'number', 'created_at']
    queryset = Room.objects.none()


    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsStaffWithAccountant()]
    

    @extend_schema(summary="Barcha klinika xonalar.", responses={200: RoomListSerializer(many=True)}, tags=["Room"])
    def get(self, request):
        cache_key = f"room_list_{request.query_params.urlencode()}"
        data = cache.get(cache_key)

        if data is None:
            room = Room.objects.select_related('department', 'department__branch').filter(is_active = True).order_by('name')

            for backend in self.filter_backends:
                room = backend().filter_queryset(request, room, self)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(room, request)
            serializer = RoomListSerializer(page, many=True)

            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=60 * 6)

        return Response(data, status=status.HTTP_200_OK)
    


    @extend_schema(summary="Yangi xona yaratish", request=RoomSerializer, responses={201: RoomSerializer}, tags=["Room"])
    def post(self, request):
        serializer = RoomSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("room_list_*")
            logger.info(f"[CREATE] Room '{serializer.data['name']}' - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class RoomDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Room.objects.none()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsStaffWithAccountant()]
        return [IsAdmin()]
    

    def get_object(self, pk):
        try:
            return Room.objects.select_related('department', 'department__branch').get(pk=pk, is_active=True)
        except Room.DoesNotExist:
            return None
        
    
    @extend_schema(summary="Xona ma'lumotlari", responses={200: RoomSerializer}, tags=["Room"])
    def get(self, request, pk):
        room = self.get_object(pk)

        if room is None:
            return Response({"detail": "Xona topilmadi."},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @extend_schema(summary="Xonalar yangilash", request=RoomSerializer, responses={200: RoomSerializer}, tags=["Room"])
    def put(self, request, pk):
        room = self.get_object(pk)

        if room is None:
            return Response({"detail": "Xona  topilmadi."},
                             status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("room_list_*")
            logger.info(f"[UPDATE] room '{room.name}' (id={pk}) — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    @extend_schema(summary="Xonalarni o'chirish", responses={200: None}, tags=["Room"])
    def delete(self, request, pk):
        room = self.get_object(pk)

        if room is None:
            return Response({"detail": "O'chirish uchun xona topilmadi."},
                            status=status.HTTP_404_NOT_FOUND)
        
        room.is_active = False
        room.save(update_fields=['is_active'])

        cache.delete_pattern("room_list_*")
        logger.info(f"[SOFT DELETE] Room '{room.name}' (id={pk}) — user: {request.user}")
        return Response({'detail': "Xona muvaffaqiyatli yopildi."}, status=status.HTTP_200_OK)
