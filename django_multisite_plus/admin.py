# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.admin import SiteAdmin as DjangoSiteAdmin
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from multisite.admin import AliasInline as MultisiteAliasInline
from multisite.models import Alias

from . import models


class SiteInline(admin.StackedInline):
    model = models.Site
    min_num = 1
    max_num = 1
    extra = 0
    fieldsets = [
        (None, {'fields': [
            'slug',
            'real_domain',
            'is_enabled',
        ]}),
    ]
    if settings.DJANGO_MULTISITE_PLUS_MODE == 'multi-process':
        fieldsets[0][1]['fields'].append('extra_uwsgi_ini')

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False

    def get_readonly_fields(self, request, obj=None):
        if not settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS:
            return super(SiteInline, self).get_readonly_fields(request, obj)
        return ['slug', 'real_domain', 'is_enabled', 'extra_uwsgi_ini']


class AliasInline(MultisiteAliasInline):
    def has_delete_permission(self, *args, **kwargs):
        if settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS:
            return False
        return super(AliasInline, self).has_delete_permission(*args, **kwargs)

    def has_add_permission(self, *args, **kwargs):
        if settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS:
            return False
        return super(AliasInline, self).has_add_permission(*args, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if not settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS:
            return super(AliasInline, self).get_readonly_fields(request, obj)
        return ['domain', 'site', 'is_canonical', 'redirect_to_canonical']


class SiteAdmin(DjangoSiteAdmin):
    list_display = (
        'domain_html',
        'linked_url',
        'real_domain',
        'slug',
        'id',
        'is_enabled',
    )
    ordering = (
        'id',
    )
    actions = (
        'update_site_action',
    )
    readonly_fields = (
        'linked_url',
    )
    fieldsets = (
        (None, {'fields': (
            ('domain', 'linked_url', 'name'),
        )}),
    )
    inlines = [
        SiteInline,
        AliasInline,
    ]

    def has_delete_permission(self, *args, **kwargs):
        if settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS:
            return False
        return super(SiteAdmin, self).has_delete_permission(*args, **kwargs)

    def has_add_permission(self, *args, **kwargs):
        if settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS:
            return False
        return super(SiteAdmin, self).has_add_permission(*args, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if not settings.DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS:
            return super(SiteAdmin, self).get_readonly_fields(request, obj)
        return ['domain', 'linked_url', 'name']

    def get_queryset(self, request):
        qs = super(SiteAdmin, self).get_queryset(request)
        return qs.prefetch_related('multisiteplus_site')

    def real_domain(self, obj):
        return obj.multisiteplus_site.real_domain
    real_domain.short_description = _('real domain')
    real_domain.admin_order_field = 'multisiteplus_site__real_domain'

    def slug(self, obj):
        return obj.multisiteplus_site.slug
    slug.short_description = _('slug')
    slug.admin_order_field = 'multisiteplus_site__slug'

    def domain_html(self, obj):
        return '{}'.format(obj.domain)
    domain_html.short_description = _('domain')
    domain_html.admin_order_field = 'domain'
    domain_html.allow_tags = True

    def linked_url(self, obj, text=_('open')):
        return '<a href="{}" target="_blank">{}</a>'.format(
            obj.multisiteplus_site.get_url(),
            text,
        )
    linked_url.short_description = _('url')
    linked_url.allow_tags = True

    def is_enabled(self, obj):
        return obj.multisiteplus_site.is_enabled
    is_enabled.short_description = _('is enabled')
    is_enabled.admin_order_field = 'multisiteplus_site__is_enabled'
    is_enabled.boolean = True

    def update_site_action(self, request, queryset):
        for obj in queryset:
            try:
                obj.multisiteplus_site.update_site()
            except models.Site.DoesNotExist:
                pass


# Instead of having 3 different entries on django admin (multisite.alias, multisite_plus.site and sites.site),
# lets merge this into a more powerful sites.site. The latter was chosen in order to avoid problems where this
# is kind of hardcoded, such as https://github.com/divio/django-cms/blob/develop/cms/cms_toolbars.py#L120
admin.site.unregister(Alias)
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)
