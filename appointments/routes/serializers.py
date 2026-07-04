from rest_framework import serializers
from django.utils import timezone

from accounts.models import User
from patients.models import Patient
from organizations.models import Room
from appointments.models import Appointment, Queue, Visit



class DoctorMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone_number']


    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    


class PatientMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.user.firs_name} {obj.user.last_name}"
    

class RoomMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'number', 'name']



class AppointmentListSerializer(serializers.ModelSerializer):
    patient = PatientMiniSerializer(read_only = True)
    doctor = DoctorMiniSerializer(read_only = True)
    room = RoomMiniSerializer(read_obly = True)
    status_display = serializers.CharField(source = "get_status_display", read_only = True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'doctor',
            'room',
            "scheduled_at",
            "status",
            "status_display",
            "reason",
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset = Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset = User.objects.filter(role = 'DOCTOR'))
    room = serializers.PrimaryKeyRelatedField(queryset = Room.objects.all(), required = False, allow_null = True)

    patient_detail = PatientMiniSerializer(source = 'patient', read_only = True)
    doctor_detail = DoctorMiniSerializer(source = 'doctor', read_only = True)
    room_detail = RoomMiniSerializer(source = 'room', read_only = True)
    status_display = serializers.CharField(source = 'get_status_display', read_only = True)


    class Meta:
        model = Appointment
        fields = [
            'id',
            "patient",
            "patient_detail",
            "doctor",
            "doctor_detail",
            "room",
            "room_detail",
            "scheduled_at",
            "status",
            "status_display",
            "reason",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["status", "created_at", "updated_at"]

        def validate_schedulet_at(self, value):
            if value < timezone.now():
                raise serializers.ValidationError(
                    "Uchrashuv vaqti o'tgan vaqtda bo'lishi mumkin emas.")
            return value
        
        def validate(self, attrs):
            doctor = attrs.get('doctor', getattr(self.instamce, 'doctor', None))
            scheduet_ad = attrs.get('scheduled_at', getattr(self.istance, 'scheduled_at', None))

            if doctor and scheduet_ad:
                qs = Appointment.objects.filter(doctor=doctor, scheduet_ad=scheduet_ad)
                
                if self.instance:
                    qs = qs.exclude(pk=self.instance.pk)
                
                if qs.exists():
                    raise serializers.ValidationError({"scheduled_at": "Bu shifokor shu vaqtda band!"})
                return attrs
            


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status']

    ALLOWED_TRANSITIONS = {
        Appointment.Status.SCHEDULED: {Appointment.Status.WAITING, Appointment.Status.CANCELLED},
        Appointment.Status.WAITING: {Appointment.Status.IN_PROGRESS, Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW},
        Appointment.Status.IN_PROGRESS: {Appointment.Status.COMPLETED},
        Appointment.Status.COMPLETED: set(),   # yakuniy holat, undan chiqib bo'lmaydi
        Appointment.Status.CANCELLED: set(),
        Appointment.Status.NO_SHOW: set(),
    }
 
    def validate_status(self, value):
        current = self.instance.status
        allowed = self.ALLOWED_TRANSITIONS.get(current, set())
        if value not in allowed and value != current:
            raise serializers.ValidationError(
                f"'{current}' holatidan '{value}' holatiga o'tib bo'lmaydi."
            )
        return value
    

class QueueListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Queue
        fields = [
            "id",
            "queue_number",
            "status",
            "called_at",
            "patient_name",
            "doctor_name",
        ]

        def get_patient(self, obj):
            return str(obj.appointment.patient)
        
        def get_doctor_name(self, obj):
            return str(obj.appointment.doctor)
        


class QueueSerializer(serializers.ModelSerializer):
    appointment = AppointmentListSerializer(read_only=True)
 
    class Meta:
        model = Queue
        fields = ["id", "appointment", "queue_number", "status", "called_at"]
        read_only_fields = ["queue_number", "called_at"]



class VisitSerializer(serializers.ModelSerializer):
    appointment = AppointmentListSerializer(read_only=True)
    duration_minutes = serializers.ReadOnlyField()
 
    class Meta:
        model = Visit
        fields = [
            "id",
            "appointment",
            "started_at",
            "ended_at",
            "duration_minutes",
            "complaints",
            "notes",
        ]
        read_only_fields = ["started_at", "ended_at", "duration_minutes"]




class VisitCloseSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(required=False, allow_blank=True)
 
    def save(self, **kwargs):
        visit = self.context["visit"]
        if "notes" in self.validated_data:
            visit.notes = self.validated_data["notes"]
            visit.save(update_fields=["notes"])
        visit.close()
        return visit