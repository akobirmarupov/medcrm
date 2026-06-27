from pathlib import Path
from datetime import timedelta
from decouple import config
import os
import dj_database_url

from dotenv import load_dotenv
from django.templatetags.static import static

load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-c%f%u_8%lxutfg9hn+eo6xc+big=uhujt*p6ef7kh#_1)otvch'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['mentix.onrender.com', '*']

CSRF_TRUSTED_ORIGINS = [
    'https://c87089dbf506e1bd-84-94-248.serveousercontent.com',
]
# AUTH_USER_MODEL = 'accounts.Users'
AUTH_USER_MODEL = 'accounts.User'

# Application definition

DJANGO_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",


    'jazzmin',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'accounts',
    'common',
    'organizations',
]

EXTERNAL_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'drf_yasg',
    "drf_spectacular",
]


INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "static"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


#redis cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = 'static/'

# Loyihaning ildizidagi (root) static papkasini tanitish:
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Frontend ilova URL manzili (emaildagi tasdiqlash havolasi uchun)
FRONTEND_URL = "https://Marketol.com"



SPECTACULAR_SETTINGS = {
    "TITLE": "MedCRM API",
    "DESCRIPTION": "Tibbiy klinika boshqaruv tizimi",
    "VERSION": "1.0.0",
}




SWAGGER_SETTINGS = {
    'DEFAULT_API_URL': 'https://c87089dbf506e1bd-84-94-248.serveousercontent.com',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'USE_SESSION_AUTH': False,
}


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    
    "DEFAULT_THROTTLE_RATES": {
        "login": "5/minute",
        "register": "3/minute",
        "anon_burst": "30/minute",
        "auth_burst": "60/minute",
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_CODE_TTL_SECONDS = 300


# Frontend ilova URL manzili (emaildagi tasdiqlash havolasi uchun)
FRONTEND_URL = "https://zentaskob.uz"


UNFOLD = {
    "SITE_TITLE": "MedCore CRM Admin",
    "SITE_HEADER": "MedCore",
    "SITE_SUBHEADER": "Klinika boshqaruv tizimi",
    "SITE_URL": "/",
    "SITE_SYMBOL": "medical_services",
    "BORDER_RADIUS": "16px",
    "THEME": "dark",  # To'q rangli interfeysni asosiy qilish

    "SITE_LOGO": {
        "light": "/static/images/logo.png",
        "dark": "/static/images/logo.png",
    },

    # =========================================================================
    #  DIZAYNNI MUKAMMAL QILISH VA UNIFOLD CLASSLARINI BUZIB O'TISH (CSS INJECTION)
    # =========================================================================
    "STYLES": {
        "css": [
            lambda request: """
                /* 1. TEPA CHAP TARAFDAGI LOGOTIPNI KATTA VA CHIROYLI YUMOLOQ QILISH */
                html body div.flex.items-center.gap-4 img.unfold-logo,
                html body .unfold-sidebar header img,
                html body a[href="/admin/"] img {
                    width: 70px !important;
                    height: 70px !important;
                    max-width: 70px !important;
                    max-height: 70px !important;
                    min-width: 70px !important;
                    min-height: 70px !important;
                    object-fit: cover !important;
                    border-radius: 50% !important; /* Mutloq dumaloq */
                    border: 3px solid #10b981 !important; /* Neon yashil hoshiya */
                    box-shadow: 0 0 15px rgba(16, 185, 129, 0.4) !important; /* Atrofdagi yorug'lik */
                    margin: 15px auto !important;
                    display: block !important;
                }

                /* Standart mitti sozlamalar ikonkasi chiqib turgan blokni yashirish yoki logoga joy ochish */
                html body div.flex.items-center.gap-4 .material-symbols-outlined {
                    display: none !important;
                }
                
                /* 2. HAR BIR APP VA MODELLARNI ALOHIDA JOZIBALI RAMKALARGA SOLISH */
                /* Asosiy paneldagi har bitta blok (Accounts, Auth va h.k.) */
                html body main .grid > div,
                html body main div[class*="shadow"] {
                    background-color: #1a2333 !important; /* Premium quyuq ko'k-kulrang */
                    border: 2px solid #2e3b52 !important; /* Elegant ramka chizig'i */
                    border-radius: 20px !important; /* Burchaklar yumaloqligi */
                    padding: 24px !important;
                    margin-bottom: 30px !important;
                    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3) !important;
                }

                /* Ramka ichidagi modellarning qatorlari (Rows) */
                html body main .grid > div table,
                html body main .grid > div div[class*="border-b"] {
                    background: #151c2c !important;
                    border-radius: 12px !important;
                    overflow: hidden;
                    border: 1px solid #243146 !important;
                }

                /* 3. LOGIN SAHIFASIDAGI LOGOTIPNI MAKSIMAL KATTA QILISH */
                html body div[class*="login"] img, 
                html body .unfold-login-box img {
                    width: 130px !important;
                    height: 130px !important;
                    max-width: 130px !important;
                    max-height: 130px !important;
                    border-radius: 50% !important;
                    border: 4px solid #10b981 !important;
                    box-shadow: 0 0 25px rgba(16, 185, 129, 0.5) !important;
                    margin: 0 auto 30px auto !important;
                }

                /* 4. CHAP TARAFI SIDEBAR VA NAVIGATSIYA DIZAYNI */
                html body .unfold-sidebar {
                    background-color: #0f141c !important; /* To'qroq sidebar */
                    border-right: 1px solid #1e293b !important;
                }
                
                /* Navigatsiyadagi guruh sarlavhalari */
                html .unfold-sidebar-section-title {
                    color: #10b981 !important;
                    font-weight: 700 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.05em !important;
                    border-left: 3px solid #10b981 !important;
                    padding-left: 10px !important;
                }
            """
        ],
    },

    # --- SIZ XOOHLAGAN TAYYOR YANGI IKONKALAR VA STRUKTURA ---
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False, # Tartibsiz chiqmasligi uchun o'zimiz ramkalaymiz
        
        "navigation": [
    {
        "title": "Asosiy Dashboard",
        "separator": True,
        "items": [
            {"title": "Bosh sahifa", "icon": "space_dashboard", "link": "/admin/"},
        ],
    },
    {
        "title": "Foydalanuvchilar (Accounts)",
        "separator": True,
        "collapsible": False,
        "items": [
            {"title": "Xodimlar (Users)", "icon": "group", "link": "/admin/accounts/user/"},
            {"title": "Profillar (Profiles)", "icon": "contact_page", "link": "/admin/accounts/profile/"},
        ],
    },
    {
        "title": "Tashkilot (Organizations)",
        "separator": True,
        "collapsible": False,
        "items": [
            {"title": "Klinikalar", "icon": "local_hospital", "link": "/admin/organizations/clinic/"},
            {"title": "Filiallar", "icon": "account_balance", "link": "/admin/organizations/branch/"},
            {"title": "Bo'limlar", "icon": "meeting_room", "link": "/admin/organizations/department/"},
            {"title": "Xonalar", "icon": "door_front", "link": "/admin/organizations/room/"},
        ],
    },
    {
        "title": "Xavfsizlik Tizimi",
        "separator": True,
        "collapsible": True,
        "items": [
            {"title": "Guruhlar", "icon": "shield_person", "link": "/admin/auth/group/"},
            {"title": "API Tokenlar", "icon": "key", "link": "/admin/authtoken/tokenproxy/"},
        ],
    },
],
    },
}



CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        # Redis uchun:
        # "BACKEND": "django.core.cache.backends.redis.RedisCache",
        # "LOCATION": "redis://127.0.0.1:6379/1",
    }
}

ESKIZ_EMAIL    = os.getenv("ESKIZ_EMAIL")
ESKIZ_PASSWORD = os.getenv("ESKIZ_PASSWORD")
ESKIZ_SENDER   = os.getenv("ESKIZ_SENDER")