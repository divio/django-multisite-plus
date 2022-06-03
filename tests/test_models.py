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
    "domain,rewrite,expected",
    [
        ("test.com", None, "test.com"),
        ("test.com", False, "test.com"),
        ("test.com", True, "slug.rewritten.com"),
        ("", None, "slug.rewritten.com"),
        ("", False, "slug.rewritten.com"),
        ("", True, "slug.rewritten.com"),
    ],
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


def test_auto_populate_sites(db, settings):
    assert not models.Site.objects.exists()
    settings.DJANGO_MULTISITE_PLUS_SITES = {
        "test-site-1": {
            "id": 1,
            "real_domain": "real-domain-for-site-1.com",
            "name": "Test Site 1",
        },
        "test-site-2": {
            "id": 2,
            "real_domain": "real-domain-for-site-2.com",
        },
    }

    models.Site.objects.auto_populate_sites()

    assert models.Site.objects.count() == 2

    site1 = models.Site.objects.get(pk=1)
    assert site1.slug == "test-site-1"
    assert site1.real_domain == "real-domain-for-site-1.com"
    assert site1.site.name == "Test Site 1"

    site2 = models.Site.objects.get(pk=2)
    assert site2.slug == "test-site-2"
    assert site2.real_domain == "real-domain-for-site-2.com"
    assert site2.site.name == ""
