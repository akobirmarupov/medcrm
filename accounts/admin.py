from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User, Profile


# ──────────────────────────────────────────────
#  Inline: Profile → User ichida ko'rsatish
# ──────────────────────────────────────────────
class ProfileInline(TabularInline):
    model = Profile
    extra = 0
    can_delete = False
    verbose_name = "Profil"
    verbose_name_plural = "Profil ma'lumotlari"
    fields = ("address", "birth_date", "avatar")
    show_change_link = True


# ──────────────────────────────────────────────
#  User Admin
# ──────────────────────────────────────────────
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "role",
        "email",
        "is_confirmed",
        "is_staff",
    )
    list_filter = ("role", "is_confirmed", "is_staff", "is_superuser")
    search_fields = ("phone_number", "first_name", "last_name", "email")
    ordering = ("phone_number",)

    inlines = [ProfileInline]

    fieldsets = (
        (
            _("Kirish ma'lumotlari"),
            {
                "classes": ["tab"],
                "fields": ("phone_number", "password"),
            },
        ),
        (
            _("Shaxsiy ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("first_name", "last_name", "email"),
            },
        ),
        (
            _("Klinika sozlamalari"),
            {
                "classes": ["tab"],
                "fields": ("role", "is_confirmed", "otp_code", "otp_expires_at"),
            },
        ),
        (
            _("Ruxsatlar"),
            {
                "classes": ["tab"],
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Muhim sanalar"),
            {
                "classes": ["tab"],
                "fields": ("last_login", "date_joined"),
            },
        ),
    )

    add_fieldsets = (
        (
            _("Asosiy ma'lumotlar"),
            {
                "classes": ["wide"],
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "email",
                ),
            },
        ),
        (
            _("Klinika sozlamalari"),
            {
                "classes": ["wide"],
                "fields": ("role", "is_confirmed"),
            },
        ),
        (
            _("Parol"),
            {
                "classes": ["wide"],
                "fields": ("password1", "password2"),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "username" in form.base_fields:
            form.base_fields["username"].widget.attrs["autofocus"] = False
        return form


# ──────────────────────────────────────────────
#  Profile Admin
# ──────────────────────────────────────────────
@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    # "avatar" o'rniga "avatar_thumbnail" — rasmni ko'rsatadi
    list_display = ("avatar_thumbnail", "user", "address", "birth_date")
    search_fields = (
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "address",
    )
    ordering = ("user",)

    fieldsets = (
        (
            _("Foydalanuvchi"),
            {
                "classes": ["tab"],
                "fields": ("user",),
            },
        ),
        (
            _("Qo'shimcha ma'lumotlar"),
            {
                "classes": ["tab"],
                "fields": ("address", "birth_date", "avatar"),
            },
        ),
    )

    # ── Kichik doira rasm (list sahifasida) ──────────────
    @admin.display(description="Avatar")
    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" '
                'style="width:48px; height:48px; object-fit:cover; '
                'border-radius:50%; border:2px solid #6366f1;" />',
                obj.avatar.url,
            )
        # Avatar yo'q bo'lsa — placeholder
        return format_html(
            '<div style="width:48px; height:48px; border-radius:50%; '
            'background:#374151; display:flex; align-items:center; '
            'justify-content:center; font-size:20px; color:#9ca3af;">👤</div>'
        )