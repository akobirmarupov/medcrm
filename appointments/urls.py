from django.urls import path

from appointments.routes.appointment_view import AppointmentListCreateAPIView, AppointmentDetailAPIView


urlpatterns = [
    # Qabullar
    path('appointment/', AppointmentListCreateAPIView.as_view(), name='appointment-list-create'),
    path('appointment/<int:pk>/', AppointmentDetailAPIView.as_view(), name='appointment-detail'),
]