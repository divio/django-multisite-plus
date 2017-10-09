# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import django.apps


class AppConfig(django.apps.AppConfig):

    name = 'django_multisite_plus'
    verbose_name = 'Multisite+'

    def ready(self):
        from django.conf import settings
        from django.db.utils import ProgrammingError, OperationalError
        Site = self.get_model('Site')
        try:
            if getattr(settings, 'DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES', True):
                print('Syncing django_multisite_plus Sites based on settings')
                Site.objects.auto_populate_sites()

            if getattr(settings, 'DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS', True):
                print('Rewriting django.contrib.sites.Site based on local settings')
                Site.objects.update_sites()
                # Make sure django-multisite is synced.
                # Sometimes (e.g when loading fixtures) the signals don't fire and the
                # Aliases get out of sync.
                print('Syncing multisite.Alias based on Sites')
                from multisite.models import Alias
                Alias.canonical.sync_all()
        except (ProgrammingError, OperationalError):
            # ProgrammingError:
            # database is not ready yet. Maybe we're in the migrate
            # management command.
            # OperationalError:
            # Many parallel processes might have created deadlocks, e.g when
            # starting up uwsgi with many workers.
            pass
