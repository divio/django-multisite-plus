# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import os

from aldryn_addons.utils import boolean_ish

env = os.environ.get

UWSGI_DEFAULT_DOMAIN = env('DJANGO_MULTISITE_PLUS_UWSGI_DEFAULT_DOMAIN')
UWSGI_BASE_SOCKETS_DIR = env('DJANGO_MULTISITE_PLUS_UWSGI_BASE_SOCKETS_DIR', '/app/uwsgi/tmp/vassal-sockets/')
UWSGI_BASE_CONFIG_DIR = env('DJANGO_MULTISITE_PLUS_UWSGI_BASE_CONFIG_DIR', '/app/uwsgi/')
UWSGI_ALIAS_DOMAIN_MAPPING_DIR = env('DJANGO_MULTISITE_PLUS_UWSGI_ALIAS_DOMAIN_MAPPING_DIR', '/app/uwsgi/tmp/aliases/')

UWSGI_LOCAL_TEST_MODE = boolean_ish(env('DJANGO_MULTISITE_PLUS_UWSGI_LOCAL_TEST_MODE'))
UWSGI_LOCAL_TEST_KEY = env('DJANGO_MULTISITE_PLUS_UWSGI_LOCAL_TEST_KEY')
