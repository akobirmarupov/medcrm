"""
appointments/models.py

Ushbu app klinikadagi navbat va qabul jarayonini boshqaradi:
- Appointment: bemor uchun shifokorga belgilangan uchrashuv
- Queue: real vaqtdagi navbat holati (WAITING / CALLED / ...)
- Visit: shifokor bemorni chaqirgandan keyingi haqiqiy qabul jarayoni
"""

from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils import timezone

from common.models import BaseModel
from patients.models import Patient
from organizations.models import Room

User = settings.AUTH_USER_MODEL


class SoftDeleteModel(BaseModel):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])


class ActiveManager(models.Manager):
    """Default manager — faqat is_deleted=False yozuvlarni qaytaradi."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Appointment(SoftDeleteModel):
    """
    Bemor uchun shifokorga, xonaga va vaqtga belgilangan uchrashuv.

    Vazifasi:
    - Receptionist tomonidan yaratiladi (bemor + shifokor + vaqt + sabab).
    - Butun Patient Flow'ning boshlanish nuqtasi: Queue va Visit
      shu Appointment atrofida quriladi (OneToOne orqali).
    """

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Rejalashtirilgan"
        WAITING = "WAITING", "Navbatda"
        IN_PROGRESS = "IN_PROGRESS", "Jarayonda"
        COMPLETED = "COMPLETED", "Yakunlangan"
        CANCELLED = "CANCELLED", "Bekor qilingan"
        NO_SHOW = "NO_SHOW", "Kelmadi"

    patient = models.ForeignKey(Patient,on_delete=models.PROTECT,related_name="appointments",)
    doctor = models.ForeignKey(User,on_delete=models.PROTECT,related_name="appointments",limit_choices_to={"role": "DOCTOR"},)
    room = models.ForeignKey(Room,on_delete=models.SET_NULL,null=True,blank=True,related_name="appointments",)
    scheduled_at = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.SCHEDULED,db_index=True,)
    reason = models.CharField(max_length=255)
    objects = ActiveManager()
    all_objects = models.Manager()  # soft-delete qilinganlarni ham ko'rish uchun

    class Meta:
        ordering = ["scheduled_at"]
        indexes = [
            models.Index(fields=["doctor", "scheduled_at"]),
            models.Index(fields=["status", "scheduled_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "scheduled_at"],
                condition=models.Q(is_deleted=False),
                name="unique_doctor_schedule_slot",
            )
        ]

    def __str__(self):
        return f"{self.patient} -> {self.doctor} ({self.scheduled_at:%Y-%m-%d %H:%M})"

    def clean(self):
        if self.scheduled_at and self.scheduled_at < timezone.now():
            raise ValidationError("Appointment vaqti o'tmishda bo'lishi mumkin emas.")
        
        if self.doctor_id and self.doctor.role != "DOCTOR":
            raise ValidationError("Tanlangan foydalanuvchi DOCTOR roliga ega emas.")


class Queue(SoftDeleteModel):
    """
    Har bir Appointment uchun real vaqtdagi navbat holati.

    Vazifasi:
    - Receptionist appointment yaratganda Queue ham avtomatik yaratiladi
      (odatda signal yoki service layer orqali), queue_number beriladi.
    - Doctor bemorni chaqirganda call_patient() chaqiriladi, status=CALLED
      bo'ladi va called_at yoziladi.
    - Bu model tez-tez o'qiladigan va tez-tez yangilanadigan "jonli" ma'lumot
      — shuning uchun oldingi suhbatda aytganimdek, uni agressiv cache
      qilish xavfli (staleness = real muammo).
    """

    class Status(models.TextChoices):
        WAITING = "WAITING", "Kutmoqda"
        CALLED = "CALLED", "Chaqirilgan"
        SKIPPED = "SKIPPED", "O'tkazib yuborilgan"
        DONE = "DONE", "Tugallangan"

    appointment = models.OneToOneField(Appointment,on_delete=models.CASCADE,related_name="queue",)
    queue_number = models.PositiveIntegerField()
    called_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.WAITING,db_index=True,)
    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ["queue_number"]
        indexes = [
            models.Index(fields=["status", "queue_number"]),
        ]

    def __str__(self):
        return f"Navbat #{self.queue_number} - {self.get_status_display()}"

    def call_patient(self):
        self.status = self.Status.CALLED
        self.called_at = timezone.now()
        self.save(update_fields=["status", "called_at"])


class Visit(SoftDeleteModel):
    """
    Shifokor bemorni chaqirgandan keyingi haqiqiy qabul jarayoni.
    """

    appointment = models.OneToOneField(Appointment,on_delete=models.CASCADE,related_name="visit",)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    complaints = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Visit: {self.appointment} ({self.started_at:%Y-%m-%d %H:%M})"

    @property
    def duration_minutes(self):
        if self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds() // 60)
        return None

    def close(self):
        self.ended_at = timezone.now()
        self.save(update_fields=["ended_at"])
        self.appointment.status = Appointment.Status.COMPLETED
        self.appointment.save(update_fields=["status"])