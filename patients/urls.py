from django.urls import path
from patients.routes.patient_record.views import(
    PatientListCreateAPIView, PatientDetailAPIView,
    MedicalRecordListCreateAPIView, MedicalRecordDetailAPIView
)
from patients.routes.allergy_chronic.views import (
    PatientAllergyListCreateAPIView, PatientAllergyDetailAPIView
)



urlpatterns = [
    # Clinic
    path('patient/', PatientListCreateAPIView.as_view(), name='patient-list-create'),
    path('patient/<int:pk>/', PatientDetailAPIView.as_view(), name='patient-detail'),

    # Branch
    path('medical_record/', MedicalRecordListCreateAPIView.as_view(), name='medical_record-list-create'),
    path('medical_record/<int:pk>/', MedicalRecordDetailAPIView.as_view(), name='medical_record-detail'),

    #allergy
    path('allergy/', PatientAllergyListCreateAPIView.as_view(), name='allergy-list-create'),
    path('allergy/<int:pk>/', PatientAllergyDetailAPIView.as_view(), name='allergy-detail'),
]