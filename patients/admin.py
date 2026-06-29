from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import Patient, MedicalRecord, PatientAllergy, PatientChronicDisease


# ──────────────────────────────────────────────
#  Inlines
# ──────────────────────────────────────────────
class PatientAllergyInline(TabularInline):
    model = PatientAllergy
    extra = 0
    verbose_name = "Allergiya"
    verbose_name_plural = "Allergiyalar"
    fields = ("allergen", "severity", "reaction", "notes")
    show_change_link = True


class PatientChronicDiseaseInline(TabularInline):
    model = PatientChronicDisease
    extra = 0
    verbose_name = "Surunkali kasallik"
    verbose_name_plural = "Surunkali kasalliklar"
    fields = ("disease_name", "icd_code", "diagnosed_at", "is_active", "notes")
    show_change_link = True


class MedicalRecordInline(TabularInline):
    model = MedicalRecord
    extra = 0
    verbose_name = "Tibbiy yozuv"
    verbose_name_plural = "Tibbiy yozuvlar"
    fields = ("title", "doctor", "notes", "attachment")
    show_change_link = True
    readonly_fields = ("created_at",)


# ──────────────────────────────────────────────
#  Patient Admin
# ──────────────────────────────────────────────
@admin.register(Patient)
class PatientAdmin(ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone_number",
        "blood_type",
        "pinfl",
        "insurance_number",
        "created_at",
    )
    list_filter = ("blood_type",)
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__phone_number",
        "pinfl",
        "insurance_number",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    inlines = [MedicalRecordInline, PatientAllergyInline, PatientChronicDiseaseInline]

    fieldsets = (
        (
            _("Foydalanuvchi"),
            {
                "classes": ["tab"],
                "fields": ("user",),
            },
        ),
        (
            _("Tibbiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("blood_type", "pinfl", "insurance_number"),
            },
        ),
        (
            _("Favqulodda aloqa"),
            {
                "classes": ["tab"],
                "fields": ("emergency_contact_name", "emergency_contact_phone"),
            },
        ),
        (
            _("Qo'shimcha"),
            {
                "classes": ["tab"],
                "fields": ("notes", "created_at", "updated_at"),
            },
        ),
    )


# ──────────────────────────────────────────────
#  MedicalRecord Admin
# ──────────────────────────────────────────────
@admin.register(MedicalRecord)
class MedicalRecordAdmin(ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "title",
        "created_at",
    )
    list_filter = ("doctor",)
    search_fields = (
        "patient__user__first_name",
        "patient__user__last_name",
        "doctor__first_name",
        "doctor__last_name",
        "title",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("Asosiy"),
            {
                "classes": ["tab"],
                "fields": ("patient", "doctor", "title"),
            },
        ),
        (
            _("Tafsilotlar"),
            {
                "classes": ["tab"],
                "fields": ("notes", "attachment"),
            },
        ),
        (
            _("Sana"),
            {
                "classes": ["tab"],
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


# ──────────────────────────────────────────────
#  PatientAllergy Admin
# ──────────────────────────────────────────────
@admin.register(PatientAllergy)
class PatientAllergyAdmin(ModelAdmin):
    list_display = (
        "id",
        "patient",
        "allergen",
        "severity",
        "reaction",
    )
    list_filter = ("severity",)
    search_fields = (
        "patient__user__first_name",
        "patient__user__last_name",
        "allergen",
        "reaction",
    )
    ordering = ("severity",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("Bemor"),
            {
                "classes": ["tab"],
                "fields": ("patient",),
            },
        ),
        (
            _("Allergiya ma'lumotlari"),
            {
                "classes": ["tab"],
                "fields": ("allergen", "severity", "reaction", "notes"),
            },
        ),
        (
            _("Sana"),
            {
                "classes": ["tab"],
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


# ──────────────────────────────────────────────
#  PatientChronicDisease Admin
# ──────────────────────────────────────────────
@admin.register(PatientChronicDisease)
class PatientChronicDiseaseAdmin(ModelAdmin):
    list_display = (
        "id",
        "patient",
        "disease_name",
        "icd_code",
        "diagnosed_at",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = (
        "patient__user__first_name",
        "patient__user__last_name",
        "disease_name",
        "icd_code",
    )
    ordering = ("-diagnosed_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("Bemor"),
            {
                "classes": ["tab"],
                "fields": ("patient",),
            },
        ),
        (
            _("Kasallik ma'lumotlari"),
            {
                "classes": ["tab"],
                "fields": ("disease_name", "icd_code", "diagnosed_at", "is_active"),
            },
        ),
        (
            _("Qo'shimcha"),
            {
                "classes": ["tab"],
                "fields": ("notes", "created_at", "updated_at"),
            },
        ),
    )