# -*- coding: utf-8 -*-
from aldryn_client import forms


class Form(forms.BaseForm):
    rewrite_domains = forms.CheckboxField(
        'Rewrite Site.domain based on '
        'DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT and the site slug. '
        'This is only the default value. '
        'Override it with the DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS '
        'environment variable.',
        required=False,
        initial=True,
    )
    rewrite_domain_format = forms.CharField(
        'Default url format for auto populated domain. '
        'The default is "{}.divio.me". '
        'Override it with the '
        'DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT environment variable.',
        initial='{}.divio.me',
        required=False,
    )
    auto_populate_sites = forms.CheckboxField(
        'Auto populate the Sites in the database with values from the '
        'DJANGO_MULTISITE_PLUS_SITES setting. Override with the '
        'DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES environment variable.',
        initial=True,
        required=False,
    )

    def to_settings(self, data, settings):
        # django-multisite annoyingly requires a working database and cache
        # at import time. So in "build" mode (used for collectstatic at build
        # time) we don't configure it.
        # Also if the CACHE_URL is locmem (used when calling
        # createcachetable) we ignore multisite.
        # TODO: find solutions upstream in django-multisite to prevent this
        #       awkward CACHE_URL "if" situation.
        from aldryn_addons.utils import djsenv as env
        DJANGO_MODE = env('DJANGO_MODE')
        if DJANGO_MODE == 'build' and settings['CACHE_URL'] == 'locmem://':
            return settings

        from multisite import SiteID
        settings['SITE_ID'] = SiteID(default=1)
        MIDDLEWARE_CLASSES = settings['MIDDLEWARE_CLASSES']
        INSTALLED_APPS = settings['INSTALLED_APPS']
        INSTALLED_APPS.append('multisite')
        INSTALLED_APPS.append('django_multisite_plus')

        # multisite.middleware.DynamicSiteMiddleware must be before
        # cms.middleware.utils.ApphookReloadMiddleware
        MIDDLEWARE_CLASSES.insert(
            MIDDLEWARE_CLASSES.index(
                'cms.middleware.utils.ApphookReloadMiddleware'),
            'django_multisite_plus.middlewares.DynamicSiteMiddleware',
        )

        # djangocms_multisite.middleware.CMSMultiSiteMiddleware must be after
        # cms.middleware.utils.ApphookReloadMiddleware
        MIDDLEWARE_CLASSES.insert(
            MIDDLEWARE_CLASSES.index(
                'cms.middleware.utils.ApphookReloadMiddleware')+1,
            'djangocms_multisite.middlewares.CMSMultiSiteMiddleware',
        )

        settings['DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS'] = env(
            'DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS',
            data['rewrite_domains'],
        )
        settings['DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT'] = env(
            'DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT',
            data['rewrite_domain_format'] or '{}.divio.me',
        )
        settings['DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES'] = env(
            'DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES',
            data['auto_populate_sites'],
        )
        settings['DJANGO_MULTISITE_PLUS_SITES'] = env(
            'DJANGO_MULTISITE_PLUS_SITES',
            {},
        )

        # djangocms-multisite has it's own version of cms urls that cache
        # correctly. This will no longer be necessary for cms versions that
        # include https://github.com/divio/django-cms/pull/5832
        settings['ADDON_URLS_I18N_LAST'] = 'django_multisite_plus.cms_urls'

        return settings
