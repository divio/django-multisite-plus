# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
import django.contrib.sites.admin
import django.contrib.sites.models

from . import models


class SiteInline(admin.StackedInline):
    model = models.Site
    can_delete = False
    min_num = 1
    fieldsets = (
        (None, {'fields': (
            'slug',
            'real_domain',
        )}),
    )


class SiteAdmin(django.contrib.sites.admin.SiteAdmin):
    list_display = (
        'domain_html',
        'real_domain',
        'slug',
        'id',
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
            ('domain', 'linked_url'),
        )}),
    )
    inlines = [
        SiteInline,
    ] + django.contrib.sites.admin.SiteAdmin.inlines

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
        return '{} {}'.format(
            obj.domain,
            self.linked_url(obj),
        )
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

    def update_site_action(self, request, queryset):
        for obj in queryset:
            try:
                obj.multisiteplus_site.update_site()
            except models.Site.DoesNotExist:
                pass


# admin.site.unregister(django.contrib.sites.models.Site)
# admin.site.register(django.contrib.sites.models.Site, SiteAdmin)
admin.site.register(models.DjangoContribSite, SiteAdmin)


# class SiteAdmin(admin.ModelAdmin):
#     list_display = (
#         'slug',
#         'real_domain',
#     )
# admin.site.register(Site, SiteAdmin)
