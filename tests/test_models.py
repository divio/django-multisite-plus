import pytest

from django_multisite_plus import models


@pytest.mark.parametrize(
    "format,slug,expected",
    [
        ("{}.mydomain.com", "myslug", "myslug.mydomain.com"),
        ("subdomain.{}.com", "otherslug", "subdomain.otherslug.com"),
    ],
)
def test_domain_for_slug(settings, format, slug, expected):
    assert models.domain_for_slug(slug, format) == expected
    settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT = format
    assert models.domain_for_slug(slug) == expected


@pytest.mark.parametrize(
    "domain,rewrite,expected", [
        ("test.com", None, "test.com"),
        ("test.com", False, "test.com"),
        ("test.com", True, "slug.rewritten.com"),
        ("", None, "slug.rewritten.com"),
        ("", False, "slug.rewritten.com"),
        ("", True, "slug.rewritten.com"),
    ]
)
def test_site_domain(settings, djangosite, domain, rewrite, expected):
    settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT = "{}.rewritten.com"
    if rewrite is None:
        delattr(settings, "DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS")
    else:
        settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS = rewrite

    site = models.Site(site=djangosite, real_domain=domain, slug="slug")
    assert site.domain == expected


def test_site_update_site(djangosite):
    site = models.Site(site=djangosite, real_domain="test.com", slug="test")
    assert djangosite.domain == "example.com"

    site.update_site()
    assert djangosite.domain == "test.com"

    # A second run shall have no effect
    site.update_site()
    assert djangosite.domain == "test.com"
