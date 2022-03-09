import os
import secrets


SECRET_KEY = secrets.token_urlsafe(48)

INSTALLED_APPS = [
    "django.contrib.sites",
    "django_multisite_plus",
]

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
