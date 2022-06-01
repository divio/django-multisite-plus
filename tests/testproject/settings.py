import os
import secrets


SECRET_KEY = secrets.token_urlsafe(48)

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "multisite",
    "django_multisite_plus",
]

SITE_ID = 1

ROOT_URLCONF = "testproject.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "USER": "postgres",
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_5432_TCP_PORT"],
    }
}

DJANGO_MULTISITE_PLUS_MODE = "single-process"

DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES = False
DJANGO_MULTISITE_PLUS_AUTO_REWRITE_DOMAINS = False
