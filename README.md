# 🏥 MedCRM

**MedCRM** is a comprehensive healthcare management system designed to automate patient registration, appointments, medical records, laboratory workflows, prescriptions, billing, and reporting for clinics and medical centers.

---

## 🛠 Tech Stack

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.x-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.x-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-SimpleJWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Gmail](https://img.shields.io/badge/Gmail_SMTP-OTP-EA4335?style=for-the-badge&logo=gmail&logoColor=white)
---

## 📦 Required Libraries

```
django
djangorestframework
djangorestframework-simplejwt
psycopg2-binary
redis
django-redis
python-decouple
python-dotenv
drf-yasg
drf-spectacular
django-cors-headers
Pillow
whitenoise
django-unfold
```

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/medcrm.git
cd medcrm

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env

# 5. Run migrations
python manage.py migrate

# 6. Start Redis
sudo systemctl start redis-server

# 7. Run the server
python manage.py runserver
```

---

## 🔐 Environment Variables

```env
DB_NAME=medcrm_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432

EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_CODE_TTL_SECONDS=300

ESKIZ_EMAIL=your@gmail.com
ESKIZ_PASSWORD=your_password
ESKIZ_SENDER=4546
```

---

## 🔴 Redis Cache

OTP kodlar Redis da vaqtinchalik saqlanadi:

- OTP yuborilganda → `cache.set(otp_key, code, timeout=300)` — 5 daqiqa
- OTP tasdiqlanganda → `cache.delete(otp_key)` — o'chiriladi
- 5 daqiqa ichida tasdiqlanmasa → avtomatik o'chadi

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}
```

---

## 🔑 Authentication

JWT token asosida autentifikatsiya:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

## 📡 API Endpoints

### 🔐 Auth

| Method | Endpoint | Description |
|---|---|---|
| POST | `/account/auth/register/` | Ro'yxatdan o'tish (OTP email yuboriladi) |
| POST | `/account/verify-otp/` | OTP kodni tasdiqlash → User yaratiladi |
| POST | `/account/auth/login/` | Login → JWT access & refresh token |

### 🔒 Forgot Password

| Method | Endpoint | Description |
|---|---|---|
| POST | `/account/forgot-password/` | Email orqali OTP yuborish |
| POST | `/account/forgot-password/verify/` | OTP tasdiqlash → reset JWT token |
| POST | `/account/forgot-password/confirm/` | Yangi parol o'rnatish (Bearer token) |

---

## 🔄 Registration Flow

```
POST /register/
      ↓
Serializer validatsiya
      ↓
cache.set() → Ma'lumot 5 daqiqaga Redis da saqlanadi
      ↓
Email yuboriladi (OTP kod)
      ↓
POST /verify-otp/ → OTP to'g'ri → User DB ga yoziladi ✅
```

## 🔄 Forgot Password Flow

```
POST /forgot-password/ → OTP email yuboriladi
      ↓
POST /forgot-password/verify/ → OTP tasdiqlash → JWT reset token qaytaradi
      ↓
POST /forgot-password/confirm/ → Bearer token + yangi parol → Parol yangilanadi ✅
```

---

## 👤 User Model

`AbstractUser` asosida kengaytirilgan model:

| Field | Type | Description |
|---|---|---|
| `phone_number` | CharField | Login uchun (unique) |
| `email` | EmailField | OTP tasdiqlash uchun |
| `role` | CharField | ADMIN, DOCTOR, NURSE, RECEPTIONIST, PATIENT, ACCOUNTANT |
| `is_confirmed` | BooleanField | Email tasdiqlangan? |
| `otp_code` | CharField | OTP kod |
| `otp_expires_at` | DateTimeField | OTP muddati |

---

## 🛡 Permissions

`common/permissions.py` da `BasePermission` asosida role-based permissions:

- `BasePermission` — DRF da foydalanuvchining API resurslariga kirish huquqini tekshirish uchun asosiy klass
- `getattr` — obyekt ichidagi xususiyatni nomi orqali xavfsiz va dinamik tarzda olish (`user.role` ning xavfsiz varianti)

---

## 📝 Development Notes

Hozirgi bosqichda ikki xil ro'yxatdan o'tish varianti ko'rib chiqilmoqda:

1. **Variant 1 (Oddiy):** Ism, familiya, telefon raqam va parol — login telefon raqam orqali, tasdiqlamasiz
2. **Variant 2 (Email OTP):** Yuqoridagi ma'lumotlarga qo'shimcha email orqali OTP tasdiqlash

Qaysi variant ishlatilishi **klinika boshlig'i bilan kelishilgandan** keyin aniqlanadi.

---

## 📚 API Documentation

```
/swagger/   → Swagger UI
/redoc/     → ReDoc UI
```

---

## 👨‍💻 Author

**Akobir Marupov** — Backend Developer