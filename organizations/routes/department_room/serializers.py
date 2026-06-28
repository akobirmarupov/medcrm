# organizations/routes/department/serializers.py

from rest_framework import serializers
from organizations.models import Department, Room
from accounts.models import User


class BranchShortSerializer(serializers.Serializer):
    id   = serializers.IntegerField()
    name = serializers.CharField()


class HeadDoctorSerializer(serializers.Serializer):
    id         = serializers.IntegerField()
    full_name  = serializers.SerializerMethodField()
    phone_number      = serializers.CharField()

    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name}"



class DepartmentListSerializer(serializers.ModelSerializer):
    branch_name      = serializers.CharField(source='branch.name', read_only=True)
    head_doctor_name = serializers.SerializerMethodField()

    class Meta:
        model  = Department
        fields = [
            'id',
            'name',
            'branch_name',
            'head_doctor_name',
            'is_active',
        ]

    def get_head_doctor_name(self, obj):
        if obj.head_doctor:
            return f"{obj.head_doctor.last_name} {obj.head_doctor.first_name}"
        return None


class DepartmentSerializer(serializers.ModelSerializer):
    branch      = BranchShortSerializer(read_only=True)
    head_doctor = HeadDoctorSerializer(read_only=True)
    rooms_count = serializers.SerializerMethodField()
    branch_id      = serializers.PrimaryKeyRelatedField(
        queryset=Department._meta.get_field('branch').related_model.objects.all(),
        source='branch',
        write_only=True
    )
    head_doctor_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),source='head_doctor',write_only=True,required=False,allow_null=True)

    class Meta:
        model  = Department
        fields = [
            'id',
            'name',
            'description',
            'branch',        # read
            'branch_id',     # write
            'head_doctor',   # read
            'head_doctor_id',# write
            'rooms_count',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_rooms_count(self, obj):
        return obj.rooms.filter(is_active=True).count()



class DepartmentShortSerializer(serializers.Serializer):
    id   = serializers.IntegerField()
    name = serializers.CharField()


class RoomListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    branch_name     = serializers.CharField(source='department.branch.name', read_only=True)
    room_type_label = serializers.CharField(source='get_room_type_display', read_only=True)

    class Meta:
        model  = Room
        fields = [
            'id',
            'number',
            'name',
            'room_type',
            'room_type_label',
            'floor',
            'capacity',
            'department_name',
            'branch_name',
            'is_active',
        ]


class RoomSerializer(serializers.ModelSerializer):
    department      = DepartmentShortSerializer(read_only=True)
    room_type_label = serializers.CharField(source='get_room_type_display', read_only=True)

    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        source='department',
        write_only=True
    )

    class Meta:
        model  = Room
        fields = [
            'id',
            'number',
            'name',
            'room_type',
            'room_type_label',
            'floor',
            'capacity',
            'department',    # read
            'department_id', # write
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        department = attrs.get('department', getattr(self.instance, 'department', None))
        number     = attrs.get('number',     getattr(self.instance, 'number', None))

        qs = Room.objects.filter(department=department, number=number, is_active=True)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError({
                'number': f"'{number}' raqamli xona bu bo'limda allaqachon mavjud."
            })

        return attrs