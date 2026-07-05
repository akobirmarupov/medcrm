from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, StackedInline

from .models import Appointment, Queue, Visit


# ──────────────────────────────────────────────
#  Inline: Queue → Appointment ichida (OneToOne)
# ──────────────────────────────────────────────
class QueueInline(StackedInline):
    model = Queue
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = "Navbat"
    verbose_name_plural = "Navbat"
    fields = ("queue_number", "status", "called_at")
    readonly_fields = ("called_at",)


# ──────────────────────────────────────────────
#  Inline: Visit → Appointment ichida (OneToOne)
# ──────────────────────────────────────────────
class VisitInline(StackedInline):
    model = Visit
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = "Qabul (Visit)"
    verbose_name_plural = "Qabul (Visit)"
    fields = ("started_at", "ended_at", "complaints", "notes")
    readonly_fields = ("started_at",)


# ──────────────────────────────────────────────
#  Appointment Admin
# ──────────────────────────────────────────────
@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    list_display = (
        "patient",
        "doctor",
        "room",
        "scheduled_at",
        "status",
        "is_deleted",
    )
    list_filter = ("status", "is_deleted", "doctor", "room")
    search_fields = (
        "patient__user__first_name",
        "patient__user__last_name",
        "doctor__first_name",
        "doctor__last_name",
        "reason",
    )
    ordering = ("-scheduled_at",)
    autocomplete_fields = ("patient", "doctor", "room")
    readonly_fields = ("created_at", "updated_at", "deleted_at")

    # doctor'ni faqat role=DOCTOR bo'lgan userlar bilan cheklash
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "doctor":
            kwargs["queryset"] = db_field.related_model.objects.filter(role="DOCTOR")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    inlines = [QueueInline, VisitInline]

    fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("patient", "doctor", "room"),
            },
        ),
        (
            _("Vaqt va sabab"),
            {
                "classes": ["tab"],
                "fields": ("scheduled_at", "reason"),
            },
        ),
        (
            _("Holat"),
            {
                "classes": ["tab"],
                "fields": ("status", "is_deleted", "deleted_at"),
            },
        ),
        (
            _("Audit"),
            {
                "classes": ["tab"],
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


# ──────────────────────────────────────────────
#  Queue Admin
# ──────────────────────────────────────────────
@admin.register(Queue)
class QueueAdmin(ModelAdmin):
    list_display = (
        "queue_number",
        "get_patient",
        "get_doctor",
        "status",
        "called_at",
        "is_deleted",
    )
    list_filter = ("status", "is_deleted")
    search_fields = (
        "appointment__patient__user__first_name",
        "appointment__patient__user__last_name",
        "appointment__doctor__first_name",
        "appointment__doctor__last_name",
    )
    ordering = ("queue_number",)
    autocomplete_fields = ("appointment",)
    readonly_fields = ("created_at", "updated_at", "deleted_at")

    @admin.display(description="Bemor")
    def get_patient(self, obj):
        return obj.appointment.patient

    @admin.display(description="Shifokor")
    def get_doctor(self, obj):
        return obj.appointment.doctor

    fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("appointment", "queue_number"),
            },
        ),
        (
            _("Holat"),
            {
                "classes": ["tab"],
                "fields": ("status", "called_at", "is_deleted", "deleted_at"),
            },
        ),
        (
            _("Audit"),
            {
                "classes": ["tab"],
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


# ──────────────────────────────────────────────
#  Visit Admin
# ──────────────────────────────────────────────
@admin.register(Visit)
class VisitAdmin(ModelAdmin):
    list_display = (
        "get_patient",
        "get_doctor",
        "started_at",
        "ended_at",
        "duration_minutes",
        "is_deleted",
    )
    list_filter = ("is_deleted",)
    search_fields = (
        "appointment__patient__user__first_name",
        "appointment__patient__user__last_name",
        "complaints",
    )
    ordering = ("-started_at",)
    autocomplete_fields = ("appointment",)
    readonly_fields = ("created_at", "updated_at", "deleted_at", "duration_minutes")

    @admin.display(description="Bemor")
    def get_patient(self, obj):
        return obj.appointment.patient

    @admin.display(description="Shifokor")
    def get_doctor(self, obj):
        return obj.appointment.doctor
    
    def get_queryset(self, request):
        qs = self.model.all_objects.all()  # is_deleted filtrini chetlab o'tadigan manager
        return qs

    fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("appointment", "started_at", "ended_at", "duration_minutes"),
            },
        ),
        (
            _("Tibbiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("complaints", "notes"),
            },
        ),
        (
            _("Holat"),
            {
                "classes": ["tab"],
                "fields": ("is_deleted", "deleted_at"),
            },
        ),
        (
            _("Audit"),
            {
                "classes": ["tab"],
                "fields": ("created_at", "updated_at"),
            },
        ),
    )