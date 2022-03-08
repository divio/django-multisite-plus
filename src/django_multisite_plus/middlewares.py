# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys

# Py2 and Py3 compatible reload
from imp import reload

from django.conf import settings

import multisite.middleware
from multisite.models import Alias

from djangocms_multisite import middleware


class CMSMultiSiteMiddleware(middleware.CMSMultiSiteMiddleware):

    def process_request(self, request):
        super(CMSMultiSiteMiddleware, self).process_request(request)

        if 'django_multisite_plus.cms_urls' in sys.modules:
            reload(sys.modules['django_multisite_plus.cms_urls'])


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
