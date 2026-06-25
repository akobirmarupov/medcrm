from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import BaseModel
from django.utils.crypto import get_random_string
from django.utils import timezone
import datetime
from .manager import CustomUserManager


# class Users(AbstractUser, BaseModel):
#     ADMIN = 'ADMIN'
#     DOCTOR = 'DOCTOR'
#     NURSE = 'NURSE'
#     RECEPTIONIST = 'RECEPTIONIST'
#     PATIENT = 'PATIENT'
#     ACCOUNTANT = 'ACCOUNTANT'

#     ROLE_CHOICES = [
#         (ADMIN, 'Admin'),
#         (DOCTOR, 'Doctor'),
#         (NURSE, 'Nurse'),
#         (RECEPTIONIST, 'Receptionist'),
#         (PATIENT, 'Patient'),
#         (ACCOUNTANT, 'Accountant'),
#     ]

#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PATIENT)
#     first_name = models.CharField(max_length=150, blank=False, null=False)
#     last_name = models.CharField(max_length=150, blank=False, null=False)    
#     phone_number = models.CharField(max_length=15, unique=True)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'phone_number' 
#     REQUIRED_FIELDS = ['first_name', 'last_name'] 

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.phone_number})"



class User(AbstractUser, BaseModel):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    RECEPTIONIST = "RECEPTIONIST"
    PATIENT = "PATIENT"
    ACCOUNTANT = "ACCOUNTANT"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (DOCTOR, "Doctor"),
        (NURSE, "Nurse"),
        (RECEPTIONIST, "Receptionist"),
        (PATIENT, "Patient"),
        (ACCOUNTANT, "Accountant"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PATIENT)
    first_name = models.CharField(max_length=150, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    is_confirmed = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    def generate_otp(self) -> None:
        self.otp_code = get_random_string(length=6, allowed_chars="0123456789")
        self.otp_expires_at = timezone.now() + datetime.timedelta(minutes=5)
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Profil"