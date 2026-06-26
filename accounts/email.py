from __future__ import annotations

import logging
import secrets

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

_CODE_LENGTH = 6
_CACHE_PREFIX = "medcrm_otp"


def _cache_key(email: str) -> str:
    return f"{_CACHE_PREFIX}:{email.lower().strip()}"



def generate_otp_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(_CODE_LENGTH))



def send_otp_email(email: str) -> bool:

    code = generate_otp_code()

    try:
        send_mail(
                subject="MedCRM — Tasdiqlash kodi",
                message=(
                    f"Salom!\n\n"
                    f"Tizimga kirish uchun tasdiqlash kodingiz: {code}\n\n"
                    f"Kod {settings.EMAIL_CODE_TTL_SECONDS // 60} daqiqa davomida amal qiladi.\n\n"
                    f"Agar siz so'rov yubormagan bo'lsangiz, ushbu xabarni e'tiborsiz qoldiring."
                ),
                from_email=f"MedCRM <{settings.EMAIL_HOST_USER}>",  # ✅ Shu qatorni o'zgartiring
                recipient_list=[email],
                fail_silently=False,
            )
    except Exception:
        logger.exception("OTP email yuborishda xato: %s", email)
        return False

    # Email ketdi → Redis ga saqlaymiz
    cache.set(_cache_key(email), code, timeout=settings.EMAIL_CODE_TTL_SECONDS)
    logger.info("OTP yuborildi: %s", email)
    return True



def verify_otp_code(email: str, code: str) -> bool:

    cached_code = cache.get(_cache_key(email))

    if not cached_code:
        logger.warning("OTP topilmadi yoki muddati o'tgan: %s", email)
        return False

    if str(cached_code).strip() != str(code).strip():
        logger.warning("Noto'g'ri OTP kiritildi: %s", email)
        return False

    cache.delete(_cache_key(email))
    logger.info("OTP tasdiqlandi: %s", email)
    return True



def is_otp_active(email: str) -> bool:

    return cache.get(_cache_key(email)) is not None