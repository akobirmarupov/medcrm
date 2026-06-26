from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import authenticate as django_authenticate
from django.core.cache import cache
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.email import send_otp_email, verify_otp_code, is_otp_active
from accounts.models import User, Profile


_PENDING_REGISTER_PREFIX = "medcrm_pending_register"
_PENDING_REGISTER_TTL = 60 * 10

_RESET_PASSWORD_PREFIX = "medcrm_reset_password"
_RESET_PASSWORD_TTL = 60 * 5



@dataclass(frozen=True)
class TokenPair:
    access: str
    refresh: str


def _issue_tokens(user: User) -> TokenPair:
    """Foydalanuvchi uchun JWT token juftligini yaratadi."""
    refresh = RefreshToken.for_user(user)
    return TokenPair(
        access=str(refresh.access_token),
        refresh=str(refresh),
    )



class LoginService:
    """
    Telefon raqam + parol orqali tizimga kirish.
    """

    def login(self, *, phone_number: str, password: str) -> TokenPair:
        # Django authenticate — USERNAME_FIELD = phone_number
        user = django_authenticate(username=phone_number, password=password)

        if user is None:
            raise ValueError("Telefon raqam yoki parol noto'g'ri.")

        if not user.is_active:
            raise ValueError("Akkaunt faol emas. Administrator bilan bog'laning.")

        if not user.is_confirmed:
            raise ValueError("Akkaunt tasdiqlanmagan. Administrator bilan bog'laning.")

        return _issue_tokens(user)


class RegisterService:
    """
    Ro'yxatdan o'tish 2 bosqich:
      1. request_registration() → ma'lumotni cache ga saqlaydi, emailga OTP yuboradi
      2. confirm_registration() → OTP ni tekshiradi, User yaratadi
    """

    def request_registration(
        self,
        *,
        first_name: str,
        last_name: str,
        phone_number: str,
        email: str,
        password: str,
    ) -> None:
        # Telefon raqam allaqachon bormi?
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValueError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")

        # Email allaqachon bormi?
        if email and User.objects.filter(email=email).exists():
            raise ValueError("Bu email allaqachon ro'yxatdan o'tgan.")

        # OTP allaqachon yuborilganmi? (spam himoya)
        if is_otp_active(email):
            raise ValueError("Kod allaqachon yuborilgan. 5 daqiqa kuting.")

        # Ma'lumotni cache ga saqlaymiz
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "email": email,
            "password": password,
        }
        cache.set(
            self._pending_key(email),
            payload,
            timeout=_PENDING_REGISTER_TTL,
        )

        # Emailga OTP yuboramiz
        sent = send_otp_email(email)
        if not sent:
            cache.delete(self._pending_key(email))
            raise ValueError("Email yuborishda xato. Keyinroq urinib ko'ring.")

    @transaction.atomic
    def confirm_registration(self, *, email: str, code: str) -> TokenPair:
        # OTP tekshiramiz
        if not verify_otp_code(email, code):
            raise ValueError("Kod noto'g'ri yoki muddati o'tgan.")

        # Cache dan ma'lumotni olamiz
        payload = cache.get(self._pending_key(email))
        if not payload:
            raise ValueError("Ro'yxatdan o'tish muddati o'tgan. Qayta urinib ko'ring.")

        # Yana bir marta tekshiramiz (race condition)
        if User.objects.filter(phone_number=payload["phone_number"]).exists():
            cache.delete(self._pending_key(email))
            raise ValueError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")

        # User yaratamiz
        user = User.objects.create_user(
            phone_number=payload["phone_number"],
            email=payload.get("email") or None,
            first_name=payload["first_name"],
            last_name=payload["last_name"],
            password=payload["password"],
            is_confirmed=True,
            is_active=True,
        )

        # Profile avtomatik yaratamiz
        Profile.objects.create(user=user)

        # Cache tozalaymiz
        cache.delete(self._pending_key(email))

        return _issue_tokens(user)

    @staticmethod
    def _pending_key(email: str) -> str:
        return f"{_PENDING_REGISTER_PREFIX}:{email.lower().strip()}"



class ForgotPasswordService:
    """
    Parolni tiklash 2 bosqich:
      1. send_reset_code()  → emailga OTP yuboradi
      2. reset_password()   → OTP + yangi parol
    """

    def send_reset_code(self, *, email: str) -> None:
        # Email bazada bormi?
        if not User.objects.filter(email=email).exists():
            raise ValueError("Bu email ro'yxatdan o'tmagan.")

        # OTP allaqachon yuborilganmi?
        if is_otp_active(email):
            raise ValueError("Kod allaqachon yuborilgan. 5 daqiqa kuting.")

        sent = send_otp_email(email)
        if not sent:
            raise ValueError("Email yuborishda xato. Keyinroq urinib ko'ring.")

    @transaction.atomic
    def reset_password(self, *, email: str, code: str, new_password: str) -> None:
        # OTP tekshiramiz
        if not verify_otp_code(email, code):
            raise ValueError("Kod noto'g'ri yoki muddati o'tgan.")

        # Userni topamiz
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("Foydalanuvchi topilmadi.")

        # Yangi parolni o'rnatamiz
        user.set_password(new_password)
        user.save(update_fields=["password"])