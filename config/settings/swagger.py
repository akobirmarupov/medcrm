REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardPagination",
    "DEFAULT_THROTTLE_RATES": {
        "login": "5/minute",
        "register": "3/minute",
        "anon_burst": "30/minute",
        "auth_burst": "60/minute",
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Healthcare Management API',
    'DESCRIPTION': 'Tibbiyot boshqaruv tizimi API dokumentatsiyasi',
    'VERSION': '1.0.0',
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