from django.contrib.sites.models import Site

import pytest

from django_multisite_plus import apps
import django_multisite_plus


@pytest.fixture
def djangosite(db):
    return Site.objects.get_current()


@pytest.fixture
def appconfig():
    return apps.AppConfig("django_multisite_plus", django_multisite_plus)
