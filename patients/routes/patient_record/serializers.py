from rest_framework import serializers
from patients.models import Patient, MedicalRecord
from accounts.models import User


class PatientListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'phone_number', 'blood_type', 'pinfl']


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    birth_date = serializers.DateField(source='user.profile.birth_date', read_only=True)
    address = serializers.CharField(source='user.profile.address', read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'full_name', 'phone_number', 'birth_date', 'address',
            'blood_type', 'pinfl', 'insurance_number',
            'emergency_contact_name', 'emergency_contact_phone',
            'notes', 'created_at',
        ]
        read_only_fields = ['full_name', 'phone_number', 'birth_date', 'address', 'created_at']

    def validate_user(self, value):
        if value.role != User.PATIENT:
            raise serializers.ValidationError("Faqat PATIENT rolidagi foydalanuvchi tanlanishi mumkin.")
        if hasattr(value, 'patient') and not self.instance:
            raise serializers.ValidationError("Bu foydalanuvchining profili allaqachon mavjud.")
        return value

    def validate_pinfl(self, value):
        if value and (len(value) != 14 or not value.isdigit()):
            raise serializers.ValidationError("PINFL 14 ta raqamdan iborat bo'lishi kerak.")
        return value


class MedicalRecordListSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ['id', 'title', 'doctor_name', 'created_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'title', 'notes', 'attachment', 'created_at',
        ]
        read_only_fields = ['doctor', 'doctor_name', 'patient_name', 'created_at']

