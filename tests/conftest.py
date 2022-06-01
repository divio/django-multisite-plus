from django.contrib.sites.models import Site

import pytest


@pytest.fixture
def djangosite(db):
    return Site.objects.get_current()
