from datetime import date
import re

from rest_framework import serializers

from patients.models import Patient, PatientAllergy, PatientChronicDisease



class PatientShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = ("id", "full_name", "pinfl", "phone_number")
        read_only_fields = fields


class PatientAllergyReadSerializer(serializers.ModelSerializer):

    patient = PatientShortSerializer(read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)

    class Meta:
        model = PatientAllergy
        fields = (
            "id",
            "patient",
            "allergen",
            "severity",
            "severity_display",
            "reaction",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PatientAllergyWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientAllergy
        fields = ("id", "patient", "allergen", "severity", "reaction", "notes")
        extra_kwargs = {
            "patient": {"required": False},
        }

    def validate_allergen(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "Allergen nomi kamida 2 ta belgidan iborat bo'lishi kerak."
            )
        return value.title()

    def validate(self, attrs):
        severity = attrs.get("severity", getattr(self.instance, "severity", None))
        reaction = attrs.get("reaction", getattr(self.instance, "reaction", None))

        if severity in ("SEVERE", "LIFE_THREATENING") and not reaction:
            raise serializers.ValidationError(
                {"reaction": "Og'ir yoki hayot uchun xavfli allergiyada reaktsiya tavsifi majburiy."}
            )

        patient = attrs.get("patient") or getattr(self.instance, "patient", None)
        allergen = attrs.get("allergen") or getattr(self.instance, "allergen", None)
        if patient and allergen:
            qs = PatientAllergy.objects.filter(patient=patient, allergen__iexact=allergen)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"allergen": "Ushbu bemor uchun bu allergen allaqachon qayd etilgan."}
                )
        return attrs

    def create(self, validated_data):
        return PatientAllergy.objects.create(**validated_data)

    def to_representation(self, instance):
        return PatientAllergyReadSerializer(instance, context=self.context).data



ICD10_REGEX = re.compile(r"^[A-TV-Z][0-9][0-9AB](\.[0-9A-TV-Z]{1,4})?$")


class PatientChronicDiseaseReadSerializer(serializers.ModelSerializer):

    patient = PatientShortSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = PatientChronicDisease
        fields = (
            "id",
            "patient",
            "disease_name",
            "icd_code",
            "diagnosed_at",
            "is_active",
            "status_display",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_status_display(self, obj):
        return "Faol" if obj.is_active else "Arxiv"


class PatientChronicDiseaseWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientChronicDisease
        fields = (
            "id",
            "patient",
            "disease_name",
            "icd_code",
            "diagnosed_at",
            "is_active",
            "notes",
        )
        extra_kwargs = {
            "patient": {"required": False},
        }

    def validate_icd_code(self, value):
        if not value:
            return value
        value = value.strip().upper()
        if not ICD10_REGEX.match(value):
            raise serializers.ValidationError(
                "ICD-10 kod formati noto'g'ri (masalan: E11, I10, J45.0)."
            )
        return value

    def validate_diagnosed_at(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("Tashxis sanasi kelajakda bo'lishi mumkin emas.")
        return value

    def validate(self, attrs):
        patient = attrs.get("patient") or getattr(self.instance, "patient", None)
        icd_code = attrs.get("icd_code") or getattr(self.instance, "icd_code", None)
        if patient and icd_code:
            qs = PatientChronicDisease.objects.filter(patient=patient, icd_code=icd_code)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"icd_code": "Ushbu bemorda shu ICD-10 kodli tashxis allaqachon mavjud."}
                )
        return attrs

    def create(self, validated_data):
        return PatientChronicDisease.objects.create(**validated_data)

    def to_representation(self, instance):
        return PatientChronicDiseaseReadSerializer(instance, context=self.context).data