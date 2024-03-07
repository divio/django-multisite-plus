from django.core.exceptions import ImproperlyConfigured

import pytest


@pytest.mark.parametrize(
    "auto_populate,auto_rewrite,rewrite,should_raise",
    [
        (None, None, None, True),
        (None, None, False, True),
        (None, None, True, True),
        (None, True, None, True),
        (None, True, False, True),
        (None, True, True, True),
        (None, False, None, True),
        (None, False, False, True),
        (None, False, True, True),
        (False, None, None, True),
        (False, None, False, False),
        (False, None, True, True),
        (False, True, None, True),
        (False, True, False, True),
        (False, True, True, True),
        (False, False, None, False),
        (False, False, False, False),
        (False, False, True, False),
        (True, None, None, True),
        (True, None, False, True),
        (True, None, True, True),
        (True, True, None, True),
        (True, True, False, True),
        (True, True, True, True),
        (True, False, None, True),
        (True, False, False, True),
        (True, False, True, True),
    ],
)
def test_auto_populate_error(
    settings, appconfig, auto_populate, auto_rewrite, rewrite, should_raise
):
    if auto_populate is not None:
        settings.DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES = auto_populate
    else:
        delattr(settings, "DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES")

    if auto_rewrite is not None:
        settings.DJANGO_MULTISITE_PLUS_AUTO_REWRITE_DOMAINS = auto_rewrite
    else:
        delattr(settings, "DJANGO_MULTISITE_PLUS_AUTO_REWRITE_DOMAINS")

    if rewrite is not None:
        settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS = rewrite
    else:
        delattr(settings, "DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS")

    if should_raise:
        with pytest.raises(ImproperlyConfigured):
            appconfig.ready()
    else:
        appconfig.ready()
