<div align="center">

# 🏥 MedCRM

**MedCRM** is a comprehensive healthcare management system designed to automate patient registration, appointments, medical records, laboratory workflows, prescriptions, billing, and reporting for clinics and medical centers.

</div>


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


---
## 🏥 Clinic & Branch Management API

### Overview
This module provides a complete REST API for managing clinics and their branches within a healthcare management system. It enables authorized personnel to create, view, update, and delete clinic and branch records with role-based access control.

---

### What Was Built

**Clinic Management**
- List all registered clinics with basic info (name, phone, active status)
- Create new clinics with full details including legal name, address, contact info, logo, and license number
- Retrieve detailed clinic information including live branch count
- Update clinic details (full or partial)
- Delete clinics — only allowed when no branches are attached

**Branch Management**
- List all branches across all clinics
- Create new branches linked to a specific clinic
- Retrieve detailed branch information
- Update branch details
- Delete branches
- Automatic validation to ensure only one main branch (`is_main`) exists per clinic

---

### How It Benefits Users

- **Administrators** can fully manage clinic and branch data from a single API without touching the database directly
- **Medical staff** (doctors, nurses, receptionists, accountants) can view clinic and branch information they need for daily operations
- **Data integrity** is protected — a clinic cannot be deleted while it still has branches, preventing orphaned records
- **Main branch conflict** is automatically caught — the system rejects attempts to assign two main branches to the same clinic

---

### Technologies & Tools Used

| Tool | Purpose |
|------|---------|
| Django REST Framework | API views, serializers, response handling |
| `APIView` | Custom class-based views for full control over HTTP methods |
| `ModelSerializer` | Automatic serialization of Clinic and Branch models |
| `SerializerMethodField` | Dynamically computed `branch_count` field on clinic detail |
| Custom Permissions | Role-based access (`IsAdmin`, `IsStaffWithAccountant`) |
| `MultiPartParser` + `FormParser` | Logo file upload support alongside JSON data |
| `validate()` method | Cross-field validation for `is_main` branch uniqueness per clinic |

---

### API Endpoints

#### Clinic

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/v1/clinics/` | List all clinics | Staff + Accountant |
| POST | `/api/v1/clinics/` | Create a new clinic | Admin only |
| GET | `/api/v1/clinics/{id}/` | Retrieve clinic details | Staff + Accountant |
| PUT | `/api/v1/clinics/{id}/` | Update clinic | Admin only |
| DELETE | `/api/v1/clinics/{id}/` | Delete clinic (no branches allowed) | Admin only |

#### Branch

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/v1/branches/` | List all branches | Staff + Accountant |
| POST | `/api/v1/branches/` | Create a new branch | Admin only |
| GET | `/api/v1/branches/{id}/` | Retrieve branch details | Staff + Accountant |
| PUT | `/api/v1/branches/{id}/` | Update branch | Admin only |
| DELETE | `/api/v1/branches/{id}/` | Delete branch | Admin only |

---

### Access Control

| Role | List & View | Create, Update & Delete |
|------|:-----------:|:-----------------------:|
| ADMIN | ✅ | ✅ |
| DOCTOR | ✅ | ❌ |
| NURSE | ✅ | ❌ |
| RECEPTIONIST | ✅ | ❌ |
| ACCOUNTANT | ✅ | ❌ |
| PATIENT | ❌ | ❌ |

---

### Business Rules

- A clinic **cannot be deleted** if it has existing branches. All branches must be removed first.
- Each clinic can have **only one main branch** (`is_main: true`). The API automatically rejects duplicate main branch assignments.
- `branch_count` is a **read-only computed field** — it reflects the live count of branches linked to a clinic.
- `clinic_name` on branch responses is **read-only** — it is resolved automatically from the related clinic.
---

# 🏥 Django REST API — Klinika va Filial boshqaruvi

Bugun **Healthcare Management System** loyihasida Klinika va Filial modullari uchun to'liq REST API yozdim.

---

## 📦 Nimalarga erishdim?

✅ **CRUD** — Yaratish, O'qish, Yangilash, O'chirish
✅ **Pagination** — Sahifalash (10 tadan ko'rsatish)
✅ **Filter + Search + Ordering** — Qidirish va saralash
✅ **Cache** — Redis orqali tezlashtirish
✅ **Logging** — Kim nima qilganini kuzatish
✅ **Swagger** — Avtomatik API dokumentatsiya
✅ **Role-based permission** — Rol asosida kirish nazorati
✅ **select_related / prefetch_related** — DB optimizatsiya

---

## 🔐 Kirish nazorati

| Rol | Ko'rish | Yaratish / Yangilash / O'chirish |
|-----|:-------:|:--------------------------------:|
| ADMIN | ✅ | ✅ |
| DOCTOR | ✅ | ❌ |
| NURSE | ✅ | ❌ |
| RECEPTIONIST | ✅ | ❌ |
| ACCOUNTANT |✅ | ❌ |
| PATIENT | ❌ | ❌ |

---

## ⚙️ Ishlatilgan texnologiyalar

| Vosita | Maqsadi |
|--------|---------|
| `Django REST Framework` | API asosi |
| `APIView` | HTTP metodlarni nazorat qilish |
| `ModelSerializer` | Modelni JSON ga aylantirish |
| `django-filter` | Filter va qidirish |
| `drf-spectacular` | Swagger dokumentatsiya |
| `django-redis` | Cache |
| `SerializerMethodField` | `branch_count` — dinamik hisoblash |
| `select_related` | Branch → Clinic bir so'rovda |
| `prefetch_related` | Clinic → Branches optimizatsiya |
| `validate()` | `is_main` — bir klinikada faqat bitta bosh bino |
| `logging` | Har bir o'chirish va yaratishni log qilish |

---

## 🚀 Qanday ishlaydi?

**Cache** — har xil filter uchun har xil kalit:
```
clinics_list_?search=shifa  → alohida cache
clinics_list_?is_active=true → alohida cache
```
Ma'lumot o'zgarganda cache avtomatik tozalanadi.

**N+1 muammo hal qilindi:**
```python
# Har bir branch uchun alohida DB so'rovi o'rniga
Branch.objects.select_related('clinic').all()
# → 1 ta so'rovda hammasi keladi
```

**Biznes qoidalar:**
- Klinikada filiallari bo'lsa — o'chirib bo'lmaydi
- Har bir klinikada faqat 1 ta bosh filial (`is_main`) bo'lishi mumkin

---

## 📋 API Endpointlar

```
GET    /api/v1/clinics/          → Barcha klinikalar (filter, search, ordering)
POST   /api/v1/clinics/          → Yangi klinika (Admin)
GET    /api/v1/clinics/{id}/     → Klinika tafsiloti
PUT    /api/v1/clinics/{id}/     → Yangilash (Admin)
DELETE /api/v1/clinics/{id}/     → O'chirish (Admin)

GET    /api/v1/branches/         → Barcha filiallar
POST   /api/v1/branches/         → Yangi filial (Admin)
GET    /api/v1/branches/{id}/    → Filial tafsiloti
PUT    /api/v1/branches/{id}/    → Yangilash (Admin)
DELETE /api/v1/branches/{id}/    → O'chirish (Admin)
```

---

## 🐛 Yo'l-yo'lakay tuzatilgan xatolar

- `has_permissions` → `has_permission` *(bir harf farq — barcha permission ishlamay qolgan edi)*
- `get_object(pk)` → `get_object(self, pk)` *(self yo'qligi TypeError berardi)*
- Cache va Filter aralashib ketgani tuzatildi
- `search_fields` da `clinic` → `clinic__name` *(ForeignKey orqali qidirish)*
- `delete` da `cache.delete_pattern` qo'shildi
- `pagination_class` ikki marta yozilgani olib tashlandi

---

🔧 **Stack:** Python · Django · Django REST Framework · Redis · PostgreSQL



# 🏥 MedCRM — Patients & Medical Records Module

Klinika/shifoxona uchun mo'ljallangan **Bemorlar (Patients)** va **Tibbiy yozuvlar (Medical Records)** moduli. Ushbu modul orqali bemorlarni ro'yxatga olish, ularning tibbiy tarixini yuritish, shifokorlarning tashxis va kuzatuvlarini saqlash kabi funksiyalar amalga oshiriladi.

---

## 📌 Loyiha haqida

Bu modul **Django REST Framework (DRF)** asosida qurilgan bo'lib, real klinika tizimida ishlatiladigan rol-asoslangan ruxsatlar (role-based permissions), keshlash (caching), filtrlash, qidiruv, paginatsiya va loglash kabi production-ready funksiyalarni o'z ichiga oladi.

---

## ⚙️ Asosiy funksionalliklar

### 1. Bemorlar bilan ishlash (Patients)
- ✅ Bemorlar ro'yxatini olish (filtrlash, qidiruv, saralash, paginatsiya bilan)
- ✅ Yangi bemor yaratish
- ✅ Bemor profilini ko'rish (tafsilotlar bilan)
- ✅ Bemor ma'lumotlarini yangilash
- ✅ Bemorni o'chirish (faqat tibbiy yozuvlari bo'lmagan holatda)

### 2. Tibbiy yozuvlar bilan ishlash (Medical Records)
- ✅ Tibbiy yozuvlar ro'yxatini olish (rolga qarab filtrlangan)
- ✅ Yangi tibbiy yozuv yaratish (tashxis, kuzatuv, fayl biriktirish bilan)
- ✅ Yozuv tafsilotini ko'rish
- ✅ Yozuvni yangilash (faqat yozuvni yozgan shifokor)
- ✅ Yozuvni o'chirish

### 3. Qo'shimcha imkoniyatlar
- 🔍 **Filtrlash** — `django_filter` orqali `PatientFilter` va `MedicalRecordFilter`
- 🔎 **Qidiruv** — ism, familiya, telefon raqami, PINFL bo'yicha qidirish
- ↕️ **Saralash** — yaratilgan sana, PINFL bo'yicha
- 📄 **Paginatsiya** — `StandardPagination` orqali standartlashtirilgan sahifalash
- ⚡ **Keshlash (Redis/cache)** — ro'yxat so'rovlari 5 daqiqaga keshlanadi, yozuv yaratilganda/yangilanganda kesh avtomatik tozalanadi
- 📝 **Loglash** — har bir CREATE/UPDATE/DELETE amali `logger`orqali yoziladi (audit trail)
- 📎 **Fayl biriktirish** — `MultiPartParser` orqali tibbiy hujjat/rasm yuklash imkoniyati
- 📚 **Swagger/OpenAPI hujjatlashtirish** — `drf-spectacular` orqali har bir endpoint avtomatik hujjatlangan

---

## 👥 Rollar va ruxsatlar (Permissions)

Tizimda har bir foydalanuvchi roli (`role`) asosida turlicha huquqlarga ega:

| Rol | Bemorlar ro'yxati | Bemor yaratish | Bemor tahrirlash | Bemor o'chirish | Tibbiy yozuv ko'rish | Tibbiy yozuv yaratish | Tibbiy yozuv tahrirlash | Tibbiy yozuv o'chirish |
|---|---|---|---|---|---|---|---|---|
| **Admin** | ✅ Barchasi | ✅ | ✅ | ✅ | ✅ Barchasi | ✅ | ✅ | ✅ |
| **Receptionist (Resepshn)** | ✅ Barchasi | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Doctor (Shifokor)** | ✅ Faqat o'zi davolagan bemorlar | ❌ | ✅ | ❌ | ✅ Faqat o'zi yozgan yozuvlar | ✅ | ✅ Faqat o'zi yozgan | ❌ |
| **Patient (Bemor)** | ❌ | ❌ | ❌ | ❌ | ✅ Faqat o'ziga tegishli | ❌ | ❌ | ❌ |
| **Nurse / Accountant** | Cheklangan (kombinatsiyaga qarab) | — | — | — | — | — | — | — |

> Ruxsatlar `common.permissions` modulidagi `IsAdmin`, `IsDoctor`, `IsReceptionist`, `IsNurse`, `IsPatient`, `IsStaffWithAccountant`, `IsOwnerOrMedicalStaff` klasslari orqali boshqariladi va har bir endpoint uchun `get_permissions()` metodida moslashtiriladi.

### Rol bo'yicha real misollar:
- **Shifokor** faqat o'zi yozgan tibbiy yozuvlarni ko'radi va tahrirlay oladi — boshqa shifokorning yozuvini o'zgartira olmaydi.
- **Bemor** faqat o'z tibbiy tarixini ko'radi, boshqa bemorlarning ma'lumotlariga kira olmaydi.
- **Admin** tizimdagi barcha ma'lumotlarga to'liq kirish huquqiga ega.
- **Resepshn** yangi bemorlarni ro'yxatga oladi, lekin tibbiy yozuvlarga aralashmaydi (bu — shifokorning vazifasi).

---

## 🔐 Xavfsizlik va biznes-qoidalar

- Bemorni o'chirishdan oldin uning tibbiy yozuvlari mavjudligi tekshiriladi — agar mavjud bo'lsa, o'chirish bloklanadi (ma'lumotlar yo'qolib ketmasligi uchun):
  ```python
  if patient.medical_records.exists():
      return Response({"detail": "Bemorning tibbiy yozuvlari mavjud..."}, status=400)
  ```
- Shifokor faqat **o'zi yozgan** tibbiy yozuvni tahrirlashi mumkin (`record.doctor_id != request.user.id` tekshiruvi).
- Bemor profiliga kirishda, agar so'rov yuborayotgan foydalanuvchi `PATIENT` bo'lsa, faqat **o'z** profiliga kirish huquqi beriladi.
- `doctor` maydoni foydalanuvchi tomonidan yuborilmaydi — u avtomatik token orqali (`request.user`) biriktiriladi, bu soxta ma'lumot kiritilishining oldini oladi.

---

## 🧰 Texnologiyalar va yondashuvlar

| Texnologiya / Pattern | Maqsadi |
|---|---|
| Django REST Framework (`APIView`) | API endpointlarni qo'lda, to'liq nazorat bilan qurish |
| `django-filter` | Murakkab filtrlash logikasi (`PatientFilter`, `MedicalRecordFilter`) |
| DRF `SearchFilter`, `OrderingFilter` | Qidiruv va saralash |
| `cache` (Redis/Memcached) | Tez-tez so'raladigan ro'yxatlarni keshlash, performance optimallashtirish |
| `drf-spectacular` | Avtomatik Swagger/OpenAPI hujjatlari (`@extend_schema`) |
| `logging` | Har bir muhim amal uchun audit log (kim, qachon, nima qildi) |
| Custom Permission classes | Rol-asoslangan kirish nazorati (RBAC) |
| `select_related` | N+1 so'rov muammosini oldini olish, DB optimizatsiyasi |
| `MultiPartParser`, `FormParser`, `JSONParser` | JSON va fayl (multipart) so'rovlarini bir xil endpointda qabul qilish |

---

## 📂 API Endpointlar

### Patients
| Method | Endpoint | Tavsif | Ruxsat |
|---|---|---|---|
| `GET` | `/patient/` | Bemorlar ro'yxati | Admin, Receptionist, Doctor |
| `POST` | `/patient/` | Yangi bemor yaratish | Admin, Receptionist |
| `GET` | `/patient/<pk>/` | Bemor profili | Staff, Owner |
| `PUT` | `/patient/<pk>/` | Bemorni yangilash | Admin, Receptionist, Doctor |
| `DELETE` | `/patient/<pk>/` | Bemorni o'chirish | Admin |

### Medical Records
| Method | Endpoint | Tavsif | Ruxsat |
|---|---|---|---|
| `GET` | `/medical_record/` | Tibbiy yozuvlar ro'yxati | Admin, Doctor, Patient |
| `POST` | `/medical_record/` | Yangi yozuv yaratish | Doctor, Admin |
| `GET` | `/medical_record/<pk>/` | Yozuv tafsiloti | Admin, Doctor, Patient |
| `PUT` | `/medical_record/<pk>/` | Yozuvni yangilash | Admin, Doctor (faqat o'ziniki) |
| `DELETE` | `/medical_record/<pk>/` | Yozuvni o'chirish | Admin, Doctor |

---

## 🚀 Ishga tushirish

```bash
git clone <repo-url>
cd MedCore/medcrm
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Swagger hujjatlarini ko'rish uchun: `/api/schema/swagger-ui/`

---

## 🛣️ Keyingi rejalar (Roadmap)

- [ ] Tibbiy yozuvlarga ko'p fayl biriktirish imkoniyati
- [ ] Bemor uchun PDF formatdagi tibbiy tarix hisobotini eksport qilish
- [ ] WebSocket orqali real-time bildirishnomalar (yangi yozuv qo'shilganda)
- [ ] Unit va integration testlar qamrovini kengaytirish

---

## 👨‍💻 Muallif

Loyiha **MedCRM** tizimining bir qismi sifatida ishlab chiqilgan.

## 👨‍💻 Author

**Akobir Marupov** — Backend Developer



