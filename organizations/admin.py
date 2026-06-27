from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import Clinic, Branch, Department, Room


# ──────────────────────────────────────────────
#  Inline: Branch → Clinic ichida
# ──────────────────────────────────────────────
class BranchInline(TabularInline):
    model = Branch
    extra = 0
    can_delete = False
    verbose_name = "Filial"
    verbose_name_plural = "Filiallar"
    fields = ("name", "phone", "address", "is_main", "is_active")
    show_change_link = True


# ──────────────────────────────────────────────
#  Inline: Department → Branch ichida
# ──────────────────────────────────────────────
class DepartmentInline(TabularInline):
    model = Department
    extra = 0
    can_delete = False
    verbose_name = "Bo'lim"
    verbose_name_plural = "Bo'limlar"
    fields = ("name", "head_doctor", "is_active")
    show_change_link = True


# ──────────────────────────────────────────────
#  Inline: Room → Department ichida
# ──────────────────────────────────────────────
class RoomInline(TabularInline):
    model = Room
    extra = 0
    can_delete = False
    verbose_name = "Xona"
    verbose_name_plural = "Xonalar"
    fields = ("number", "name", "room_type", "floor", "capacity", "is_active")
    show_change_link = True


# ──────────────────────────────────────────────
#  Clinic Admin
# ──────────────────────────────────────────────
@admin.register(Clinic)
class ClinicAdmin(ModelAdmin):
    list_display = ("name", "legal_name", "phone", "email", "license_number", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "legal_name", "phone", "email", "license_number")
    ordering = ("name",)

    inlines = [BranchInline]

    fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("name", "legal_name"),
            },
        ),
        (
            _("Aloqa ma'lumotlari"),
            {
                "classes": ["tab"],
                "fields": ("phone", "email", "address"),
            },
        ),
        (
            _("Rasmiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("license_number", "logo"),
            },
        ),
        (
            _("Holat"),
            {
                "classes": ["tab"],
                "fields": ("is_active",),
            },
        ),
    )


# ──────────────────────────────────────────────
#  Branch Admin
# ──────────────────────────────────────────────
@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ("name", "clinic", "phone", "is_main", "opened_at", "is_active")
    list_filter = ("is_main", "is_active", "clinic")
    search_fields = ("name", "phone", "clinic__name")
    ordering = ("clinic", "name")

    inlines = [DepartmentInline]

    fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("clinic", "name"),
            },
        ),
        (
            _("Aloqa ma'lumotlari"),
            {
                "classes": ["tab"],
                "fields": ("phone", "address"),
            },
        ),
        (
            _("Qo'shimcha"),
            {
                "classes": ["tab"],
                "fields": ("is_main", "opened_at", "is_active"),
            },
        ),
    )


# ──────────────────────────────────────────────
#  Department Admin
# ──────────────────────────────────────────────
@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ("name", "get_clinic", "branch", "head_doctor", "is_active")
    list_filter = ("is_active", "branch__clinic")
    search_fields = ("name", "branch__name", "branch__clinic__name")
    ordering = ("branch", "name")

    @admin.display(description="Klinika")
    def get_clinic(self, obj):
        return obj.branch.clinic.name

    inlines = [RoomInline]

    fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("branch", "name", "description"),
            },
        ),
        (
            _("Boshqaruv"),
            {
                "classes": ["tab"],
                "fields": ("head_doctor", "is_active"),
            },
        ),
    )

# ──────────────────────────────────────────────
#  Room Admin
# ──────────────────────────────────────────────
@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = ("number", "name", "get_clinic", "department", "room_type", "floor", "capacity", "is_active")
    list_filter = ("room_type", "is_active", "department__branch__clinic")
    search_fields = ("number", "name", "department__name", "department__branch__clinic__name")
    ordering = ("department", "floor", "number")

    @admin.display(description="Klinika")
    def get_clinic(self, obj):
        return obj.department.branch.clinic.name

    fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("department", "number", "name"),
            },
        ),
        (
            _("Xona xususiyatlari"),
            {
                "classes": ["tab"],
                "fields": ("room_type", "floor", "capacity"),
            },
        ),
        (
            _("Holat"),
            {
                "classes": ["tab"],
                "fields": ("is_active",),
            },
        ),
    )