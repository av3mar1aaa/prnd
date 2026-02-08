"""Django 4.2 settings for the legacy PRND project.

Goal: run the existing application with minimal template/business-logic changes,
keeping the bundled SQLite database (``prnd/db``).

Security note: these settings are tuned for local debugging. If you deploy on a
server, review DEBUG/ALLOWED_HOSTS/CSRF and email settings.
"""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def _env_bool(name: str, default: bool = False) -> bool:
    """Parse common boolean env values."""
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_csv(name: str) -> list[str]:
    v = os.getenv(name, "").strip()
    if not v:
        return []
    return [item.strip() for item in v.split(",") if item.strip()]


# For production, set at least:
#   DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS
# Optional:
#   DJANGO_DEBUG, DJANGO_CSRF_TRUSTED_ORIGINS, DJANGO_SECURE_COOKIES
DEBUG = _env_bool("DJANGO_DEBUG", default=True)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "prnd-dev-secret-key-change-me")
if not DEBUG and SECRET_KEY == "prnd-dev-secret-key-change-me":
    raise RuntimeError(
        "DJANGO_SECRET_KEY is required when DJANGO_DEBUG is false (production)."
    )

ALLOWED_HOSTS = _env_csv("DJANGO_ALLOWED_HOSTS")
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
if not DEBUG and not ALLOWED_HOSTS:
    raise RuntimeError(
        "DJANGO_ALLOWED_HOSTS is required when DJANGO_DEBUG is false (production). "
        "Example: export DJANGO_ALLOWED_HOSTS='example.com,www.example.com'"
    )

LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # legacy apps
    "prnd.activity",
    "prnd.calculator",
    "prnd.register",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# If you serve the app behind HTTPS, set these to true in production:
#   export DJANGO_SECURE_COOKIES=1
_secure_cookies = _env_bool("DJANGO_SECURE_COOKIES", default=not DEBUG)
CSRF_COOKIE_SECURE = _secure_cookies
SESSION_COOKIE_SECURE = _secure_cookies

# If you deploy behind a reverse proxy that terminates TLS (nginx, Caddy, etc.),
# enable this:
#   export DJANGO_BEHIND_PROXY=1
if _env_bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = _env_csv("DJANGO_CSRF_TRUSTED_ORIGINS")

ROOT_URLCONF = "prnd.urls"
WSGI_APPLICATION = "prnd.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "tempdir")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR / "staticfiles")

# Auth
LOGIN_URL = "/prnd/accounts/login/"
LOGIN_REDIRECT_URL = "/prnd/"
LOGOUT_REDIRECT_URL = "/prnd/"

# Email: don't send real emails in local dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Password hashers: keep modern defaults.
# If your legacy DB contains very old hashes, you may need to add a legacy hasher.
