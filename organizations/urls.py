from django.urls import path
from organizations.routes.clinic_branch.views import (
    ClinicListCreateAPIView, ClinicDetailAPIView,
    BranchListCreateAPIView, BranchDetailAPIView
)
from organizations.routes.department_room.views import (
    DepartmentCreateAPIView, DepartmentDetailAPIView,
    RoomCreateAPIView, RoomDetailAPIView
)

urlpatterns = [
    # Clinic
    path('clinics/', ClinicListCreateAPIView.as_view(), name='clinic-list-create'),
    path('clinics/<int:pk>/', ClinicDetailAPIView.as_view(), name='clinic-detail'),

    # Branch
    path('branches/', BranchListCreateAPIView.as_view(), name='branch-list-create'),
    path('branches/<int:pk>/', BranchDetailAPIView.as_view(), name='branch-detail'),

    #Deportament
    path('deportament/', DepartmentCreateAPIView.as_view(), name='deportament-list-create'),
    path('deportament/<int:pk>/', DepartmentDetailAPIView.as_view(), name='deportament-detail'),

    #Room
    path('room/', RoomCreateAPIView.as_view(), name='room-list-create'),
    path('room/<int:pk>/', RoomDetailAPIView.as_view(), name='room-detail'),
]