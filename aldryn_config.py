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
    mode = forms.SelectField(
        'Process mode to use. Multi-process mode means one wsgi process per '
        'SITE_ID will be run. Single-process means a single process will be'
        'used for all sites with virtual host matching in django. Single '
        'process uses less resources. Multi-process uses much more ram, but is '
        'faster.',
        initial='single-process',
        required=True,
        choices=(
            ('single-process', 'Single Process'),
            ('multi-process', 'Multi Process (uwsgi emperor mode)'),
        )

    )

    def to_settings(self, data, settings):
        # django-multisite annoyingly requires a working database and cache
        # at import time. So in "build" mode (used for collectstatic at build
        # time) we don't configure it.
        # Also if the CACHE_URL is locmem (used when calling
        # createcachetable) we ignore multisite.
        # TODO: find solutions upstream in django-multisite to prevent this
        #       awkward CACHE_URL "if" situation.
        from aldryn_addons.utils import djsenv as env, boolean_ish
        DJANGO_MODE = env('DJANGO_MODE')
        if DJANGO_MODE == 'build' and settings['CACHE_URL'] == 'locmem://':
            return settings

        settings['INSTALLED_APPS'].append('django_multisite_plus')

        settings['DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS'] = boolean_ish(env(
            'DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS',
            data['rewrite_domains'],
        ))
        settings['DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT'] = env(
            'DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT',
            data['rewrite_domain_format'] or '{}.divio.me',
        )
        settings['DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES'] = boolean_ish(env(
            'DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES',
            data['auto_populate_sites'],
        ))
        settings['DJANGO_MULTISITE_PLUS_USE_REAL_DOMAIN'] = boolean_ish(env(
            'DJANGO_MULTISITE_PLUS_USE_REAL_DOMAIN',
            False,
        ))
        settings['DJANGO_MULTISITE_PLUS_SITES'] = env(
            'DJANGO_MULTISITE_PLUS_SITES',
            {},
        )

        mode = env('DJANGO_MULTISITE_PLUS_MODE', data['mode'])
        settings['DJANGO_MULTISITE_PLUS_MODE'] = mode
        if mode == 'single-process':
            self.single_process_settings(env, settings)
        elif mode == 'multi-process':
            self.multi_process_settings(settings)
        else:
            raise RuntimeError(
                (
                    'DJANGO_MULTISITE_PLUS_MODE must be either single-process '
                    'or multi-process. Not {}'
                ).format(mode)
            )
        return settings

    def multi_process_settings(self, settings):
        # SITE_ID is already set by aldryn-django
        # settings['SITE_ID'] = env('SITE_ID', 1)
        pass

    def single_process_settings(self, env, settings):
        from multisite import SiteID
        settings['SITE_ID'] = SiteID(default=int(env('SITE_ID', 1)))
        settings['INSTALLED_APPS'].append('multisite')

        MIDDLEWARE_CLASSES = settings['MIDDLEWARE_CLASSES']

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
            'django_multisite_plus.middlewares.CMSMultiSiteMiddleware',
        )

        # djangocms-multisite has it's own version of cms urls that cache
        # correctly. This will no longer be necessary for cms versions that
        # include https://github.com/divio/django-cms/pull/5832
        settings['ADDON_URLS_I18N_LAST'] = 'django_multisite_plus.cms_urls'
