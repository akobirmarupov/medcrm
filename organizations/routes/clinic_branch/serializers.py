from rest_framework import serializers
from organizations.models import Clinic, Branch


class ClinicSerializer(serializers.ModelSerializer):
    branch_count = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        fields = [
            'id',
            'name',
            'legal_name',
            'address',
            'phone',
            'email',
            'logo',
            'license_number',
            'is_active',
            'branch_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'branch_count']

    def get_branch_count(self, obj) -> int:
        return obj.branches.count()


class ClinicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = [
            'id',
            'name',
            'phone',
            'is_active',
        ]
        read_only_fields = ['id']


class BranchSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id',
            'clinic',
            'clinic_name',
            'name',
            'address',
            'phone',
            'is_main',
            'opened_at',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'clinic_name', 'created_at', 'updated_at']

    def validate(self, attrs):
        is_main = attrs.get('is_main', False)
        clinic = attrs.get('clinic')

        if is_main and clinic:
            qs = Branch.objects.filter(clinic=clinic, is_main=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'is_main': 'Bu klinikada bosh bino allaqachon mavjud!'
                })
        return attrs


class BranchListSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id',
            'clinic_name',
            'name',
            'phone',
            'is_main',
            'is_active',
        ]
        read_only_fields = ['id', 'clinic_name']