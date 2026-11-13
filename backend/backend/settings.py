
"""
Django settings for backend project.
"""

import os
import importlib.util
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
HAS_WHITENOISE = importlib.util.find_spec('whitenoise') is not None

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except Exception:
    pass


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {
        '1', 'true', 'yes', 'on'
    }


def env_list(name, default=''):
    return [
        item.strip()
        for item in os.getenv(name, default).split(',')
        if item.strip()
    ]


# ── Security ──────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-insecure-secret-key')
DEBUG = env_bool('DJANGO_DEBUG', True)

if DEBUG:
    ALLOWED_HOSTS = env_list(
        'DJANGO_ALLOWED_HOSTS',
        'localhost,127.0.0.1,0.0.0.0,*'
    )
else:
    ALLOWED_HOSTS = env_list(
        'DJANGO_ALLOWED_HOSTS',
        'localhost,127.0.0.1'
    )


# ── Installed Apps ────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'quiz',
    'channels',
    'corsheaders',
]


# ── ASGI / Channels / Redis ────────────────────────────────────────────────

ASGI_APPLICATION = 'backend.asgi.application'
WSGI_APPLICATION = 'backend.wsgi.application'

# Memurai is Redis-compatible and runs locally on port 6379.
# An empty or missing REDIS_URL will use this default.
REDIS_URL = (
    os.getenv('REDIS_URL') or 'redis://127.0.0.1:6379/0'
).strip()

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    }
}


# ── Authentication ────────────────────────────────────────────────────────

AUTH_USER_MODEL = 'quiz.User'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ── Middleware ────────────────────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if HAS_WHITENOISE:
    MIDDLEWARE.insert(
        1,
        'whitenoise.middleware.WhiteNoiseMiddleware'
    )


# ── Django REST Framework ─────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': os.getenv('DRF_THROTTLE_USER', '2000/day'),
        'anon': os.getenv('DRF_THROTTLE_ANON', '500/day'),
    },
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
    REST_FRAMEWORK.pop('DEFAULT_THROTTLE_RATES', None)


# ── CORS ──────────────────────────────────────────────────────────────────

FRONTEND_ORIGINS = env_list(
    'FRONTEND_ORIGINS',
    'http://localhost:3000,'
    'http://127.0.0.1:3000,'
    'http://localhost:8282,'
    'http://127.0.0.1:8282'
)

CORS_ALLOW_ALL_ORIGINS = env_bool(
    'CORS_ALLOW_ALL_ORIGINS',
    True
)

CORS_ALLOWED_ORIGINS = (
    [] if CORS_ALLOW_ALL_ORIGINS else FRONTEND_ORIGINS
)

CORS_ALLOW_CREDENTIALS = env_bool(
    'CORS_ALLOW_CREDENTIALS',
    True
)

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# ── CSRF Trusted Origins ──────────────────────────────────────────────────

CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

if DEBUG:
    CSRF_TRUSTED_ORIGINS += FRONTEND_ORIGINS

    CSRF_TRUSTED_ORIGINS += [
        'http://localhost:8080',
        'http://127.0.0.1:8080',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        f'http://{os.getenv("HOST_IP", "localhost")}:3000',
        f'http://{os.getenv("HOST_IP", "localhost")}:8282',
    ]

CSRF_TRUSTED_ORIGINS = sorted(set(CSRF_TRUSTED_ORIGINS))


# ── URLs / Templates ──────────────────────────────────────────────────────

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# ── Database ──────────────────────────────────────────────────────────────

MONGO_URI = os.getenv('MONGO_URI') or os.getenv('DATABASE_URL')

if MONGO_URI:
    DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': os.getenv('MONGO_DB_NAME', 'quiz-master'),
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': MONGO_URI,
            }
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

CONN_MAX_AGE = int(
    os.getenv('DB_CONN_MAX_AGE', '0' if MONGO_URI else '300')
)


# ── Password Validation ───────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': int(os.getenv('PASSWORD_MIN_LENGTH', '6'))
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    },
]


# ── Internationalisation ──────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True


# ── Static Files ──────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

if HAS_WHITENOISE:
    STATICFILES_STORAGE = (
        'whitenoise.storage.CompressedManifestStaticFilesStorage'
    )


# ── Media Files ───────────────────────────────────────────────────────────

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'quiz_media')


# ── Default Primary Key ───────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── Security Headers ──────────────────────────────────────────────────────

SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', False)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', False)

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False

SESSION_COOKIE_SAMESITE = os.getenv(
    'SESSION_COOKIE_SAMESITE',
    'Lax'
)

CSRF_COOKIE_SAMESITE = os.getenv(
    'CSRF_COOKIE_SAMESITE',
    'Lax'
)

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = int(
    os.getenv('SECURE_HSTS_SECONDS', '0')
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    'SECURE_HSTS_INCLUDE_SUBDOMAINS',
    False
)

SECURE_HSTS_PRELOAD = env_bool(
    'SECURE_HSTS_PRELOAD',
    False
)

SECURE_SSL_REDIRECT = env_bool(
    'SECURE_SSL_REDIRECT',
    False
)

SECURE_PROXY_SSL_HEADER = (
    'HTTP_X_FORWARDED_PROTO',
    'https'
)

USE_X_FORWARDED_HOST = env_bool(
    'USE_X_FORWARDED_HOST',
    True
)


# ── Session ───────────────────────────────────────────────────────────────

SESSION_COOKIE_AGE = int(
    os.getenv(
        'SESSION_COOKIE_AGE',
        str(int(timedelta(hours=8).total_seconds()))
    )
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool(
    'SESSION_EXPIRE_AT_BROWSER_CLOSE',
    False
)


# ── Logging ───────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name}:{lineno} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'quiz': {
            'handlers': ['console'],
            'level': os.getenv('QUIZ_LOG_LEVEL', 'INFO'),
        },
        'daphne': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
