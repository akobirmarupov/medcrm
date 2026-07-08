from django.urls import path

from appointments.routes.appointment_view import (
    AppointmentListCreateAPIView, AppointmentDetailAPIView,
    AppointmentTodayAPIView, AppointmentStatusUpdateAPIView)


urlpatterns = [
    # Qabullar
    path('appointment/', AppointmentListCreateAPIView.as_view(), name='appointment-list-create'),
    path('appointment/<int:pk>/', AppointmentDetailAPIView.as_view(), name='appointment-detail'),
    path('appointments/', AppointmentTodayAPIView.as_view(), name='appointments-list-create'),
    path('appointments/<int:pk>/', AppointmentStatusUpdateAPIView.as_view(), name='appointments-patch-detail'),
]