from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

from multisite.models import CanonicalAliasManager

from django_multisite_plus.models import SiteManager


def test_populate_sites(db):
    out = StringIO()
    with patch.object(SiteManager, "auto_populate_sites") as method:
        call_command("multisite_plus_populate_sites", stdout=out)
    method.assert_called_once_with()
    assert "Syncing django_multisite_plus" in out.getvalue()
    assert "Done." in out.getvalue()


def test_rewrite_domains(db):
    out = StringIO()
    with patch.object(SiteManager, "update_sites") as update:
        with patch.object(CanonicalAliasManager, "sync_all") as sync:
            call_command("multisite_plus_rewrite_domains", stdout=out)
    update.assert_called_once_with()
    sync.assert_called_once_with()
    assert "Rewriting django.contrib.sites.Site" in out.getvalue()
    assert "Syncing multisite.Alias" in out.getvalue()
    assert "Done." in out.getvalue()
