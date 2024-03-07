from django.contrib.sites.models import Site

import pytest

import django_multisite_plus
from django_multisite_plus import apps


@pytest.fixture
def djangosite(db):
    return Site.objects.get_current()


@pytest.fixture
def appconfig():
    return apps.AppConfig("django_multisite_plus", django_multisite_plus)
