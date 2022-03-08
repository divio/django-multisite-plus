import pytest

from django.contrib.sites.models import Site

from django_multisite_plus import models


@pytest.mark.parametrize("format,slug,expected", [
    ("{}.mydomain.com", "myslug", "myslug.mydomain.com"),
    ("subdomain.{}.com", "otherslug", "subdomain.otherslug.com"),
])
def test_domain_for_slug(settings, format, slug, expected):
    assert models.domain_for_slug(slug, format) == expected
    settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT = format
    assert models.domain_for_slug(slug) == expected


def test_site_update(db):
    djsite = Site.objects.get_current()
    site = models.Site(site=djsite, real_domain="test.com", slug="test")
    assert site.domain == "test.com"
