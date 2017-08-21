# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings

import multisite.middleware
from multisite.models import Alias


class DynamicSiteMiddleware(multisite.middleware.DynamicSiteMiddleware):
    def get_alias(self, netloc):
        """
        Returns Alias matching ``netloc``. Otherwise, the default site.
        """
        host, port = self.netloc_parse(netloc)

        try:
            alias = Alias.objects.resolve(host=host, port=port)
        except ValueError:
            alias = None

        if alias:
            return alias

        try:
            # Prefer the default SITE_ID
            site_id = settings.SITE_ID.get_default()
            alias = Alias.canonical.get(site=site_id)
        except ValueError:
            # Fallback to the first Site object
            alias = Alias.canonical.order_by('site')[0]
        return alias
