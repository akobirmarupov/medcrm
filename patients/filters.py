import django_filters as filters
from django.db import models

from patients.models import (
    Patient,
    MedicalRecord,
    PatientAllergy,
    PatientChronicDisease,
)


class PatientFilter(filters.FilterSet):
    full_name = filters.CharFilter(method="filter_full_name", label="Ism-familiya")
    first_name = filters.CharFilter(field_name="user__first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="user__last_name", lookup_expr="icontains")
    phone_number = filters.CharFilter(field_name="user__phone_number", lookup_expr="icontains")
    pinfl = filters.CharFilter(field_name="pinfl", lookup_expr="exact")
    insurance_number = filters.CharFilter(field_name="insurance_number", lookup_expr="icontains")
    blood_type = filters.ChoiceFilter(field_name="blood_type", choices=Patient.BLOOD_TYPE_CHOICES)
    has_insurance = filters.BooleanFilter(field_name="insurance_number", method="filter_has_insurance")
    created_from = filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    created_to = filters.DateFilter(field_name="created_at", lookup_expr="date__lte")

    class Meta:
        model = Patient
        fields = [
            "full_name",
            "first_name",
            "last_name",
            "phone_number",
            "pinfl",
            "insurance_number",
            "blood_type",
            "has_insurance",
            "created_from",
            "created_to",
        ]

    def filter_full_name(self, queryset, name, value):
        return queryset.filter(
            models.Q(user__first_name__icontains=value)
            | models.Q(user__last_name__icontains=value)
        )

    def filter_has_insurance(self, queryset, name, value):
        if value is True:
            return queryset.exclude(insurance_number__isnull=True).exclude(insurance_number="")
        if value is False:
            return queryset.filter(models.Q(insurance_number__isnull=True) | models.Q(insurance_number=""))
        return queryset


class MedicalRecordFilter(filters.FilterSet):
    patient = filters.NumberFilter(field_name="patient_id")
    doctor = filters.NumberFilter(field_name="doctor_id")
    patient_pinfl = filters.CharFilter(field_name="patient__pinfl", lookup_expr="exact")
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    has_attachment = filters.BooleanFilter(field_name="attachment", method="filter_has_attachment")
    created_from = filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    created_to = filters.DateFilter(field_name="created_at", lookup_expr="date__lte")

    class Meta:
        model = MedicalRecord
        fields = [
            "patient",
            "doctor",
            "patient_pinfl",
            "title",
            "has_attachment",
            "created_from",
            "created_to",
        ]

    def filter_has_attachment(self, queryset, name, value):
        if value is True:
            return queryset.exclude(attachment="").exclude(attachment__isnull=True)
        if value is False:
            return queryset.filter(models.Q(attachment="") | models.Q(attachment__isnull=True))
        return queryset


class PatientAllergyFilter(filters.FilterSet):
    patient = filters.NumberFilter(field_name="patient_id")
    allergen = filters.CharFilter(field_name="allergen", lookup_expr="icontains")
    severity = filters.ChoiceFilter(field_name="severity", choices=PatientAllergy.SEVERITY_CHOICES)
    reaction = filters.CharFilter(field_name="reaction", lookup_expr="icontains")

    class Meta:
        model = PatientAllergy
        fields = ["patient", "allergen", "severity", "reaction"]


class PatientChronicDiseaseFilter(filters.FilterSet):
    patient = filters.NumberFilter(field_name="patient_id")
    disease_name = filters.CharFilter(field_name="disease_name", lookup_expr="icontains")
    icd_code = filters.CharFilter(field_name="icd_code", lookup_expr="iexact")
    is_active = filters.BooleanFilter(field_name="is_active")
    diagnosed_from = filters.DateFilter(field_name="diagnosed_at", lookup_expr="gte")
    diagnosed_to = filters.DateFilter(field_name="diagnosed_at", lookup_expr="lte")

    class Meta:
        model = PatientChronicDisease
        fields = [
            "patient",
            "disease_name",
            "icd_code",
            "is_active",
            "diagnosed_from",
            "diagnosed_to",
        ]