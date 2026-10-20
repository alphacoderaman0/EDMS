import os
from pathlib import Path

from dotenv import load_dotenv

# Load local .env if present (Vercel injects env vars directly)
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')

DEBUG = os.getenv('DEBUG', 'False').strip().lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    '.vercel.app',
    '.now.sh',
    'localhost',
    '127.0.0.1',
]

# Django 3.2 does not support origin wildcards; build from Vercel env vars.
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
for _host in (
    os.getenv('VERCEL_URL'),
    os.getenv('VERCEL_PROJECT_PRODUCTION_URL'),
    os.getenv('CSRF_TRUSTED_ORIGIN'),  # optional full origin, e.g. https://my-app.vercel.app
):
    if not _host:
        continue
    if _host.startswith('http://') or _host.startswith('https://'):
        CSRF_TRUSTED_ORIGINS.append(_host)
    else:
        CSRF_TRUSTED_ORIGINS.append(f'https://{_host}')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'eDiary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eDiary_ManagementSystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'eDiary.context_processors.user_signup',
                'eDiary.context_processors.site_meta',
            ],
        },
    },
]

WSGI_APPLICATION = 'eDiary_ManagementSystem.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': os.getenv('DB_NAME', 'ediary'),
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': os.getenv('DATABASE_URL'),
            'tlsAllowInvalidCertificates': True,
            'tls': True,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles_build' / 'static'

# Only add project-level static dir if it exists (avoids collectstatic failures on Vercel)
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.is_dir() and any(_static_dir.iterdir()) else []

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LOGIN_URL = '/user_login'
LOGIN_REDIRECT_URL = '/user_home'
LOGOUT_REDIRECT_URL = '/'

# Email — Python 3.12-safe SMTP backend (Django 3.2 stock SMTP breaks on starttls keyfile)
_email_backend_env = os.getenv('EMAIL_BACKEND', '').strip()
if _email_backend_env in (
    '',
    'django.core.mail.backends.smtp.EmailBackend',
):
    # Default to console when SMTP host not configured; else use our fixed backend
    if os.getenv('EMAIL_HOST', '').strip():
        EMAIL_BACKEND = 'eDiary.email_backend.EmailBackend'
    else:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
elif _email_backend_env == 'django.core.mail.backends.console.EmailBackend':
    EMAIL_BACKEND = _email_backend_env
else:
    # Allow explicit override, but map stock SMTP → fixed backend
    EMAIL_BACKEND = (
        'eDiary.email_backend.EmailBackend'
        if 'smtp.EmailBackend' in _email_backend_env
        else _email_backend_env
    )

EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587') or 587)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '').strip()
# Gmail App Passwords are often copied with spaces — strip them
EMAIL_HOST_PASSWORD = (os.getenv('EMAIL_HOST_PASSWORD', '') or '').replace(' ', '').strip()
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').strip().lower() in ('true', '1', 'yes')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@ediary.local').strip()

# Cache (used for rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ediary-ratelimit',
    }
}

# Basic error logging (file). Optional Sentry if SENTRY_DSN is set.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'ediary_errors.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

_sentry_dsn = os.getenv('SENTRY_DSN', '').strip()
if _sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        sentry_sdk.init(dsn=_sentry_dsn, integrations=[DjangoIntegration()], traces_sample_rate=0.0)
    except Exception:
        pass
