from __future__ import annotations
 
import logging
 
from django.core.cache import cache
from django.utils import timezone
 
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
 
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
 
from common.permissions import IsAdmin, IsDoctor, IsNurse, IsReceptionist
from common.pagination import StandardPagination
 
from appointments.filters import AppointmentFilter
from appointments.models import Appointment, Visit
from appointments.routes.serializers import (
    AppointmentListSerializer,AppointmentSerializer,
    AppointmentStatusUpdateSerializer, VisitSerializer)


logger = logging.getLogger('appointment')



class AppointmentListCreateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    filter_backend = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['reason', 'patient__user__first_name', 'patient__user__last_name']
    ordering_fields = ['scheduled_at', 'created_at', 'status']
    queryset = Appointment.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsReceptionist()]
        return [(IsAdmin | IsReceptionist)()]
    

    @extend_schema(summary='Navbatlar ruyxati', responses={200: AppointmentListSerializer(many=True)}, tags=['Appointment'])
    def get(self, request):
        cache_key = f"appointment_list_{request.query_params.urlencode()}"
        data = cache.get(cache_key)

        if data is None:
            appointment = Appointment.objects.select_related(
                'patient__user', 'doctor', 'room').all(). order_by('-scheduled_at')
            
            for backend in self.filter_backend:
                appointment = backend().filter_queryset(request, appointment, self)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(appointment, request)
            serializer = AppointmentListSerializer(page, many=True)

            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=60*2)
        return Response(data, status=status.HTTP_200_OK)
    


    @extend_schema(summary="Yangi navbat yaratish", request=AppointmentSerializer, responses={201: AppointmentSerializer}, tags=["Appointment"])
    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern('appointment_list_*')
            logger.info(f"[CREATE] Appointment id={serializer.data['id']} — user: {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AppointmentDetailAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Appointment.objects.none()

    def get_permissions(self):
        return [(IsAdmin | IsDoctor | IsReceptionist)()]
    
    def get_object(self, pk):
        try:
            return Appointment.objects.select_related('patient__user', 'doctor', 'room').get(pk=pk)
        except Appointment.DoesNotExist:
            return None
        
    @extend_schema(summary="Navbat ma'lumotlari.", responses={200: AppointmentSerializer}, tags=['Appointment'])
    def get(self, request, pk):
        appointment = self.get_object(pk)

        if appointment is None:
            return Response({"detail": "Navbat topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.role == 'DOCTOR' and appointment.doctor_id != request.user.id:
            return Response({"detail": "Kechirasiz bu navbat sizga tegishli emas."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class AppointmentTodayAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardPagination
    queryset = Appointment.objects.none()

    def get_permissions(self):
        return [(IsAdmin | IsDoctor | IsNurse | IsReceptionist)()]
    

    @extend_schema(summary='Bugungi navbat.', responses={200: AppointmentListSerializer}, tags=['Appointment'])
    def get(self, request):
        today = timezone.localdate()
        cache_key = f"appointments_today_{today}_{request.user.role}_{request.user.id}"
        data = cache.get(cache_key)
        
        if data is None:
            #buyerda select_related bolgani sababi modelda forinekey bolgani uchun ishlatildi
            #scheduled_at__date vatqlarni kesib tashab today dagi kun oy yil bilan tenglashtirib beradi
            #order_by esa scheduled_at orqali ertalabdan boshlab kechgacha bolgan vaqtlardagi navbatlarni tartib bilan chiqaradi.
            appointment = (Appointment.objects.select_related('patient__user', 'doctor', 'room')
                           .filter(scheduled_at__date=today).order_by('scheduled_at'))

            if request.user.role == 'DOCTOR':
                appointment = appointment.filter(doctor=request.user)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(appointment, request)
            serializer = AppointmentListSerializer(page, many=True)

            data = paginator.get_paginated_response(serializer.data).data
            cache.set(cache_key, data, timeout=30)

        return Response(data, status=status.HTTP_200_OK)
    


class AppointmentStatusUpdateAPIView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Appointment.objects.none()

    def get_permissions(self):
        return [(IsDoctor | IsReceptionist)()]
    
    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return None
        
    @extend_schema(summary="Navbat statusini o'zgartirish",request=AppointmentStatusUpdateSerializer,
        responses={200: AppointmentStatusUpdateSerializer},tags=["Appointments"],)
    def patch(self, request, pk):
        appointment = self.get_object(pk)

        if appointment is None:
            return Response({"detail": "Navbat topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.role == 'DOCTOR' and appointment.doctor_id != request.user.id:
            return Response({"detail": "Bu navbat sizga tegishli emas."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AppointmentStatusUpdateSerializer(appointment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            cache.delete_pattern("appointments_list_*")
            cache.delete_pattern("appointments_today*_")
            logger.info(
                f"[STATUS] Appointment id={appointment.id} -> {appointment.status} - user: {request.user}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)