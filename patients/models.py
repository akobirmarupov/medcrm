from django.db import models
from common.models import BaseModel
from accounts.models import User



#Patient — Bemorning asosiy tibbiy ma'lumotlari (qon guruhi, PINFL, sug'urta, favqulodda aloqa)
class Patient(BaseModel):
    BLOOD_TYPE_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="patient",limit_choices_to={"role": User.PATIENT})
    blood_type = models.CharField(max_length=3,choices=BLOOD_TYPE_CHOICES,blank=True,null=True,)
    pinfl = models.CharField(max_length=14,unique=True,blank=True,null=True,help_text="14 xonali shaxsiy identifikatsiya raqami")
    insurance_number = models.CharField(max_length=50,blank=True,null=True,)
    emergency_contact_name = models.CharField(max_length=150,blank=True,null=True,help_text="Favqulodda holat uchun aloqa shaxsi")
    emergency_contact_phone = models.CharField(max_length=15,blank=True,null=True)
    notes = models.TextField(blank=True, null=True,help_text="Umumiy tibbiy eslatmalar")

    class Meta:
        verbose_name = "Bemor"
        verbose_name_plural = "Bemorlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} (PINFL: {self.pinfl or 'kiritilmagan'})"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def phone_number(self):
        return self.user.phone_number

    @property
    def birth_date(self):
        return self.user.profile.birth_date if hasattr(self.user, "profile") else None

    @property
    def address(self):
        return self.user.profile.address if hasattr(self.user, "profile") else None



#MedicalRecord — Shifokor yozgan tibbiy yozuvlar (tashxis, kuzatuvlar, fayl biriktirish)
class MedicalRecord(BaseModel):
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE,related_name="medical_records",)
    doctor = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="written_medical_records",limit_choices_to={"role": User.DOCTOR},)
    title = models.CharField(max_length=255,help_text="Yozuv sarlavhasi (masalan: Dastlabki ko'rik, Nazorat ko'rigi)",)
    notes = models.TextField(help_text="Tibbiy yozuvlar, kuzatuvlar")
    attachment = models.FileField(upload_to="medical_records/",blank=True,null=True,help_text="Qo'shimcha fayl (PDF, rasm)",
)

    class Meta:
        verbose_name = "Tibbiy yozuv"
        verbose_name_plural = "Tibbiy yozuvlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient.full_name} — {self.title} ({self.created_at.date()})"


#PatientAllergy — Bemorning allergiyalari (allergen, og'irlik darajasi, reaktsiya)
class PatientAllergy(BaseModel):
    SEVERITY_CHOICES = [
        ("MILD", "Yengil"),
        ("MODERATE", "O'rtacha"),
        ("SEVERE", "Og'ir"),
        ("LIFE_THREATENING", "Hayot uchun xavfli"),
    ]

    patient = models.ForeignKey(Patient,on_delete=models.CASCADE,related_name="allergies",)
    allergen = models.CharField(max_length=255,help_text="Allergiya sababi (masalan: Penisilin, Yong'oq)",)
    severity = models.CharField(max_length=20,choices=SEVERITY_CHOICES,default="MILD",)
    reaction = models.CharField(max_length=255,blank=True,null=True,help_text="Allergik reaktsiya (masalan: Teri toshmasi, Nafas qisilishi)",)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Allergiya"
        verbose_name_plural = "Allergiyalar"
        unique_together = ("patient", "allergen")
        ordering = ["severity"]

    def __str__(self):
        return f"{self.patient.full_name} — {self.allergen} ({self.get_severity_display()})"


#PatientChronicDisease — Surunkali kasalliklar (ICD-10 kod, tashxis sanasi, faol/arxiv holat)
class PatientChronicDisease(BaseModel):
    patient = models.ForeignKey(Patient,on_delete=models.CASCADE,related_name="chronic_diseases")
    disease_name = models.CharField(max_length=255,help_text="Kasallik nomi (masalan: Diabet, Gipertoniya)",)
    icd_code = models.CharField(max_length=10,blank=True,null=True,help_text="ICD-10 kodi (masalan: E11, I10)",)
    diagnosed_at = models.DateField(blank=True,null=True,help_text="Tashxis qo'yilgan sana",)
    is_active = models.BooleanField(default=True,help_text="Hozirda faolmi (davolanmoqdami)",)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Surunkali kasallik"
        verbose_name_plural = "Surunkali kasalliklar"
        unique_together = ("patient", "icd_code")
        ordering = ["-diagnosed_at"]

    def __str__(self):
        status = "faol" if self.is_active else "arxiv"
        return f"{self.patient.full_name} — {self.disease_name} ({status})"