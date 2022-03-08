# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.sites.models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('site', models.OneToOneField(related_name='multisiteplus_site', primary_key=True, serialize=False, to='sites.Site')),
                ('real_domain', models.CharField(default='', help_text='The real (live) domain for this site.', max_length=255, verbose_name='real domain', blank=True)),
                ('slug', models.CharField(default='', max_length=255, blank=True, help_text='Used on localdev and stage servers to build the domain together with the DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT setting.', unique=True, verbose_name='slug')),
            ],
        ),
        migrations.CreateModel(
            name='DjangoContribSite',
            fields=[
            ],
            options={
                'verbose_name': 'Site',
                'proxy': True,
                'verbose_name_plural': 'Sites',
            },
            bases=('sites.site',),
            managers=[
                ('objects', django.contrib.sites.models.SiteManager()),
            ],
        ),
    ]
