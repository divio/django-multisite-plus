# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import glob
import hashlib
import logging
import os

from django_multisite_plus import conf
from django_multisite_plus.constants import UWSGI_ALIAS_SEPARATOR

logger = logging.getLogger(__name__)


def get(key_as_bytes):
    def _get_socket(key):
        filepath = os.path.join(conf.UWSGI_ALIAS_DOMAIN_MAPPING_DIR, '{}{}*'.format(key, UWSGI_ALIAS_SEPARATOR))
        sockets = glob.glob(filepath)

        if len(sockets) > 1:
            raise RuntimeError('Multiple sockets found for key="{}" (found: "{}")'.format(key, ", ".join(sockets)))
        elif len(sockets) == 1:
            matched_domain = os.path.basename(sockets[0]).split(UWSGI_ALIAS_SEPARATOR)[1]
            # Below we use the domain hash in order to avoid filename length errors (uwsgi allows only 102 chars)
            matched_domain_hash = hashlib.md5(matched_domain.encode('utf-8')).hexdigest()
            socket_path = os.path.join(conf.UWSGI_BASE_SOCKETS_DIR, '{}.sock'.format(matched_domain_hash))
            return socket_path.encode('utf-8')
        else:
            return None

    key_as_text = key_as_bytes.decode('utf-8')

    if conf.UWSGI_LOCAL_TEST_MODE:
        if conf.UWSGI_LOCAL_TEST_KEY:
            key_as_text = conf.UWSGI_LOCAL_TEST_KEY
            logger.warn('WARNING: UWSGI_LOCAL_TEST_MODE is True! Forcing key="{}"'.format(key_as_text))
        else:
            options = glob.glob(os.path.join(conf.UWSGI_BASE_SOCKETS_DIR, '*.sock'))
            fake_sockets = {
                'localhost:8000': options[0],
                '127.0.0.1:8000': options[1],
                '0.0.0.0:8000': options[2],
            }
            fake_socket = fake_sockets[key_as_text]
            logger.warn('WARNING: UWSGI_LOCAL_TEST_MODE is True! Using test socket="{}"'.format(fake_socket))
            return fake_socket.encode('utf-8')

    preferred_socket = _get_socket(key_as_text)
    if preferred_socket:
        return preferred_socket

    if conf.UWSGI_DEFAULT_DOMAIN:
        default_socket = _get_socket(conf.UWSGI_DEFAULT_DOMAIN)
        if not default_socket:
            raise RuntimeError('Default socket not found for domain "{}".'.format(conf.UWSGI_DEFAULT_DOMAIN))
        return default_socket

    raise RuntimeError('No socket found for key "{}".'.format(key_as_text))
