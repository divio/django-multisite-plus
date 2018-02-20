# -*- coding: utf-8 -*-
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.db import models, transaction

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import django.contrib.sites.models


def domain_for_slug(slug, domain_format=None):
    domain_format = domain_format or getattr(
        settings, 'DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT', ''
    )
    return domain_format.format(slug)


class SiteManager(models.Manager):

    @transaction.atomic()
    def update_sites(self):
        sites = (
            self.select_related('site')
            .only('site', 'real_domain', 'slug')
            .select_for_update()
        )
        for site in sites:
            site.update_site()

    @transaction.atomic()
    def auto_populate_sites(self):
        sites_config = getattr(settings, 'DJANGO_MULTISITE_PLUS_SITES', {})
        for slug, data in sites_config.items():
            site_id = data.get('id')
            real_domain = data.get('real_domain')
            name = data.get('name')

            contrib_site_defaults = {}
            site_defaults = {'slug': slug}

            if real_domain:
                site_defaults['real_domain'] = real_domain
            if name:
                contrib_site_defaults['name'] = name

            if site_id:
                # A site_id was given. Use it as the primary identifier.
                try:
                    contrib_site = django.contrib.sites.models.Site.objects.get(id=site_id)
                    contrib_site_updated_fields = set()
                    for key, value in contrib_site_defaults.items():
                        if getattr(contrib_site, key) != value:
                            setattr(contrib_site, key, value)
                            contrib_site_updated_fields.add(key)
                    if contrib_site_updated_fields:
                        contrib_site.save(update_fields=contrib_site_updated_fields)
                    # We're not using update_or_create here to make sure
                    # last_updated_at does not get bumped if nothing changed.
                    # Otherwise uwsgi would keep reloading all wsgi processes
                    # (in multi-porcess mode) because it thinks the config has
                    # changed.
                    site, created = Site.objects.get_or_create(site=contrib_site, defaults=site_defaults)
                    if not created:
                        updated_fields = set()
                        for key, value in site_defaults.items():
                            if getattr(site, key) != value:
                                setattr(site, key, value)
                                updated_fields.add(key)
                        if updated_fields or contrib_site_updated_fields:
                            updated_fields.add('last_updated_at')
                            site.save(update_fields=updated_fields)

                except django.contrib.sites.models.Site.DoesNotExist:
                    domain = domain_for_slug(slug)
                    contrib_site = (
                        django.contrib.sites.models.Site.objects
                        .create(
                            id=site_id,
                            domain=domain,
                            name=name or domain,
                        )
                    )
                    site = Site.objects.create(
                        site=contrib_site,
                        slug=slug,
                        real_domain=real_domain,
                    )
            else:
                # No site_id was given. Use slug as the primary identifier.
                contrib_site = (
                    django.contrib.sites.models.Site.objects
                    .filter(multisiteplus_site__slug=slug)
                    .prefetch_related('multisiteplus_site')
                    .first()
                )
                if contrib_site:
                    updated_fields = set()
                    for key, value in contrib_site_defaults.items():
                        if getattr(contrib_site, key) != value:
                            setattr(contrib_site, key, value)
                            updated_fields.add(key)
                    if updated_fields:
                        contrib_site.save()
                    site = contrib_site.multisiteplus_site
                    contrib_site_updated_fields = set()
                    for key, value in site_defaults.items():
                        if getattr(site, key) != value:
                            setattr(site, key, value)
                            contrib_site_updated_fields.add(key)
                    if contrib_site_updated_fields:
                        site.save(update_fields=contrib_site_updated_fields)
                else:
                    domain = domain_for_slug(slug)
                    contrib_site = (
                        django.contrib.sites.models.Site.objects
                        .create(
                            domain=domain,
                            name=name or domain,
                        )
                    )
                    site = Site.objects.create(
                        site=contrib_site,
                        slug=slug,
                        real_domain=real_domain or '',
                    )


@python_2_unicode_compatible
class Site(models.Model):
    """
    This is a extension of django.contrib.sites.Site that holds extra
    information to ease multisite local and stage development/
    It holds the domain for the production version of the website and a slug
    for every Site, which is used for local development and stage
    servers (any server not using the real domains) to automatically build
    domains for every Site (e.g siteslug.dev.example.com).
    The values in here are used at startup time to update the database entries
    in django.contrib.sites.Site. This makes it easy to copy a database dump
    from one system to another and have the correct Site objects when running
    the project.
    """
    site = models.OneToOneField(
        'sites.Site',
        related_name='multisiteplus_site',
        primary_key=True,
    )
    real_domain = models.CharField(
        _('real domain'),
        max_length=255,
        blank=True, default='',
        help_text=_(
            'The real (live) domain for this site.'
        ),
    )
    slug = models.CharField(
        # FIXME: validation
        _('slug'),
        max_length=255,
        blank=True, default='',
        help_text=_(
            'Used on localdev and stage servers to build the domain together '
            'with the DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT setting.'
        ),
        unique=True,
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text=_(
            'Whether this site should be served and available.'
        )
    )
    last_updated_at = models.DateTimeField(auto_now=True)
    extra_uwsgi_ini = models.TextField(blank=True, default='')

    objects = SiteManager()

    def __str__(self):
        return force_text('{} ({})'.format(self.real_domain, self.slug))

    def get_url(self):
        return '//{}'.format(self.domain)

    @property
    def domain(self):
        rewrite = getattr(
            settings, 'DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS', False
        )
        if rewrite:
            return domain_for_slug(self.slug)
        elif not self.real_domain:
            return domain_for_slug(self.slug)
        else:
            return self.real_domain

    def update_site(self, use_real_domain=None):
        if use_real_domain is None:
            use_real_domain = getattr(settings, 'DJANGO_MULTISITE_PLUS_USE_REAL_DOMAIN', False)
        if use_real_domain:
            domain = self.real_domain
        else:
            domain = self.domain
        site = self.site
        if domain != site.domain:
            site.domain = domain
            site.save()

    def save(self, **kwargs):
        super(Site, self).save(**kwargs)
        self.update_site()


class DjangoContribSite(django.contrib.sites.models.Site):
    class Meta:
        proxy = True
        verbose_name = _('Site')
        verbose_name_plural = _('Sites')
