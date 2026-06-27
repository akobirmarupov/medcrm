from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from common.models import BaseModel
from accounts.models import User


phone_validator = RegexValidator(
    regex=r'^\+998\d{9}$', 
    message="Telefon +998XXXXXXXXX formatida bo'lishi kerak")



#Butun tizim shu klinikaga tegishli malumotlari
class Clinic(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name="Klinika nomi")
    legal_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Yuridik nomi")
    address = models.TextField(verbose_name="Manzil")
    phone = models.CharField(max_length=13, validators=[phone_validator], verbose_name="Telefon")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    logo = models.ImageField(upload_to='clinic/logos/', null=True, blank=True, verbose_name="Logotip")
    license_number = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Litsenziya raqami")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    class Meta:
        verbose_name = "Klinika"
        verbose_name_plural = "Klinikalar"

    def __str__(self):
        return self.name


#Klinikaning har bir joylashgan nuqtasi — alohida filial.
class Branch(BaseModel):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='branches', verbose_name="Klinika")
    name = models.CharField(max_length=255, verbose_name="Filial nomi")
    address = models.TextField(verbose_name="Manzil")
    phone = models.CharField(max_length=13, validators=[phone_validator], verbose_name="Telefon")
    is_main = models.BooleanField(default=False, verbose_name="Bosh bino")
    opened_at = models.DateField(null=True, blank=True, verbose_name="Ochilgan sana")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"
        constraints = [
            models.UniqueConstraint(fields=['clinic'], condition=models.Q(is_main=True), name='unique_main_branch_per_clinic')
        ]

    def __str__(self):
        return f"{self.clinic.name} — {self.name}"


#Filial ichidagi tibbiy bo'limlar.
class Department(BaseModel):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='departments', verbose_name="Filial")
    name = models.CharField(max_length=255, verbose_name="Bo'lim nomi")
    description = models.TextField(null=True, blank=True, verbose_name="Tavsif")
    head_doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments', verbose_name="Bo'lim boshlig'i")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    class Meta:
        verbose_name = "Bo'lim"
        verbose_name_plural = "Bo'limlar"

    def __str__(self):
        return f"{self.branch.name} — {self.name}"


#Bo'lim ichidagi har bir xona yoki kabinet.
class Room(BaseModel):

    class RoomType(models.TextChoices):
        CONSULTATION = 'consultation', 'Qabul xonasi'
        LABORATORY   = 'laboratory',   'Laboratoriya'
        SURGERY      = 'surgery',       'Operatsiya xonasi'
        WARD         = 'ward',          'Palata'
        PROCEDURE    = 'procedure',     'Protsedura xonasi'

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='rooms', verbose_name="Bo'lim")
    number = models.CharField(max_length=10, verbose_name="Xona raqami")
    name = models.CharField(max_length=255, verbose_name="Xona nomi")
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.CONSULTATION, verbose_name="Xona turi")
    floor = models.PositiveIntegerField(default=1, verbose_name="Qavat")
    capacity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Sig'im")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    class Meta:
        verbose_name = "Xona"
        verbose_name_plural = "Xonalar"
        constraints = [
            models.UniqueConstraint(fields=['department', 'number'], name='unique_room_number_per_department')
        ]

    def __str__(self):
        return f"{self.department.name} — {self.number}-xona"