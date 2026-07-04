import django_filters as filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Appointment, Queue, Visit

User = get_user_model()


class AppointmentFilter(filters.FilterSet):
    doctor = filters.ModelChoiceFilter(
        field_name="doctor",
        queryset=lambda request: User.objects.filter(role="DOCTOR"),
    )

    patient = filters.NumberFilter(field_name="patient_id")
    room = filters.NumberFilter(field_name="room_id")
    status = filters.ChoiceFilter(choices=Appointment.Status.choices)
    date = filters.DateFilter(field_name="scheduled_at", lookup_expr="date")
    date_from = filters.DateTimeFilter(field_name="scheduled_at", lookup_expr="gte")
    date_to = filters.DateTimeFilter(field_name="scheduled_at", lookup_expr="lte")
    search = filters.CharFilter(method="filter_search")

    class Meta:
        model = Appointment
        fields = ["doctor", "patient", "room", "status", "date", "date_from", "date_to"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(patient__user__first_name__icontains=value)
            | Q(patient__user__last_name__icontains=value)
            | Q(doctor__first_name__icontains=value)
            | Q(doctor__last_name__icontains=value)
            | Q(reason__icontains=value)
        )


class QueueFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Queue.Status.choices)
    doctor = filters.NumberFilter(field_name="appointment__doctor_id")
    room = filters.NumberFilter(field_name="appointment__room_id")
    date = filters.DateFilter(field_name="appointment__scheduled_at", lookup_expr="date")

    class Meta:
        model = Queue
        fields = ["status", "doctor", "room", "date"]


class VisitFilter(filters.FilterSet):
    doctor = filters.NumberFilter(field_name="appointment__doctor_id")
    patient = filters.NumberFilter(field_name="appointment__patient_id")
    is_open = filters.BooleanFilter(method="filter_is_open")
    date_from = filters.DateTimeFilter(field_name="started_at", lookup_expr="gte")
    date_to = filters.DateTimeFilter(field_name="started_at", lookup_expr="lte")

    class Meta:
        model = Visit
        fields = ["doctor", "patient", "is_open", "date_from", "date_to"]

    def filter_is_open(self, queryset, name, value):
        if value:
            return queryset.filter(ended_at__isnull=True)
        return queryset.filter(ended_at__isnull=False)