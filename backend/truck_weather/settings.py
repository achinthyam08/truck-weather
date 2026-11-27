"""
Django settings for truck_weather project – Milestone 1.

Reads every secret/config value from environment variables.
Copy .env.example → .env and fill in values before running.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env from the backend directory (dev convenience).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# Security
# ------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "change-me-in-production",
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1").split()

# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "truck_weather.urls"

WSGI_APPLICATION = "truck_weather.wsgi.application"

# ------------------------------------------------------------------
# CORS – frontend dev server and production origin
# ------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173 http://127.0.0.1:5173",
    ).split()
    if o.strip()
]

# ------------------------------------------------------------------
# Static files (not used in Milestone 1 but required by Django)
# ------------------------------------------------------------------
STATIC_URL = "static/"

# Plan requests carry forecast data downloaded by the browser.
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------
# REST Framework defaults
# ------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}
