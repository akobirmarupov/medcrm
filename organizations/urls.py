# organizations/clinic_branch/urls.py

from django.urls import path
from organizations.routes.clinic_branch.views import (
    ClinicListCreateAPIView, ClinicDetailAPIView,
)

urlpatterns = [
    # Clinic
    path('clinics/', ClinicListCreateAPIView.as_view(), name='clinic-list-create'),
    path('clinics/<int:pk>/', ClinicDetailAPIView.as_view(), name='clinic-detail'),

    # Branch
    # path('branches/', BranchListCreateAPIView.as_view(), name='branch-list-create'),
    # path('branches/<int:pk>/', BranchDetailAPIView.as_view(), name='branch-detail'),
]