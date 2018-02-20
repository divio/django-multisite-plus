# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import os
import subprocess
import sys

from aldryn_addons.utils import boolean_ish
from aldryn_django.cli import main, execute, web as single_process_web

import click
import yurl

from django_multisite_plus import conf
from django_multisite_plus.constants import UWSGI_ALIAS_SEPARATOR

BASE_DIR = os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

VASSALS_SQL_QUERY = ' '.join([x.strip() for x in '''
SELECT
    STRING_AGG(ma.domain, '{alias_separator}')||'.ini' ini_filename,
    CONCAT_WS(E'\\n',
        '[uwsgi]',
        'env = SITE_ID='||ds.id,
        'socket = {base_sockets_dir}'||STRING_AGG(ma.domain, '{alias_separator}')||'.sock',
        ms.extra_uwsgi_ini
    ) ini_content,
    EXTRACT('epoch' from ms.last_updated_at) last_updated
FROM
    django_multisite_plus_site AS ms
    INNER JOIN django_site as ds ON (ds.id = ms.site_id)
    INNER JOIN multisite_alias AS ma ON (ma.site_id = ms.site_id)
WHERE
    ms.is_enabled = TRUE
GROUP BY
    ds.id, ms.extra_uwsgi_ini, ms.last_updated_at;
'''.format(alias_separator=UWSGI_ALIAS_SEPARATOR, base_sockets_dir=conf.UWSGI_BASE_SOCKETS_DIR).splitlines()])


@main.command()
@click.pass_obj
@click.pass_context
def web(ctx, ctx_obj):
    if ctx_obj['settings']['DJANGO_MULTISITE_PLUS_MODE'] == 'single-process':
        ctx.invoke(single_process_web)
    else:
        execute(start_uwsgi_command(settings=ctx_obj['settings'], port=80))


def get_uwsgi_static_serving_opts(base_url, root, header_patterns):
    base_path = yurl.URL(base_url).path.lstrip('/')
    opts = [
        'static-map = /{}={}'.format(base_path, root),
        'route = {} addheader:Vary: Accept-Encoding'.format(os.path.join('^', base_path, '.*')),
    ]

    for pattern, headers in header_patterns:
        pattern = os.path.join('^', base_path, pattern)
        for k, v in headers.items():
            opts.append('route = {} addheader:{}: {}'.format(pattern, k, v))
        opts.append('route = {} last:'.format(pattern, k, v))

    return opts


def get_uwsgi_regular_opts(settings, port):
    return [
        'module = wsgi',
        'master = true',
        'workers = {}'.format(settings['DJANGO_WEB_WORKERS']),
        'max-requests = {}'.format(settings['DJANGO_WEB_MAX_REQUESTS']),
        'harakiri = {}'.format(settings['DJANGO_WEB_TIMEOUT']),
        'lazy-apps = true',
        'honour-range = true',
        'enable-threads = true',
    ]


def get_uwsgi_vassal_opts(settings, port):
    vassal_opts = get_uwsgi_regular_opts(settings, port) + [
        'chdir = /app',
        'vacuum = true',  # vacuum makes uwsgi delete sockets on exit
    ]

    if boolean_ish(os.environ.get('ENABLE_UWSGI_CHEAPER', 'on')):
        vassal_opts.extend([
            'cheaper = 1',
            'cheaper-algo = busyness',
            'cheaper-initial = 1',
            'cheaper-business-verbose = 1',
            'cheaper-business-backlog-alert = 10',
            'cheaper-overload = 20',
        ])

    if not settings['ENABLE_SYNCING']:
        serve_static = False

        if yurl.URL(settings['STATIC_URL']).host or not settings['STATIC_URL_IS_ON_OTHER_DOMAIN']:
            # TODO: we're currently starting the static url hosting on all vassals if STATIC_HOST is set.
            # We rely on the fallback for the unknown static domain to end up calling on the main vassal.
            # We should rather do this only on the main vassal or create a custom vassal just for static files.
            serve_static = True
            vassal_opts.extend(get_uwsgi_static_serving_opts(
                settings['STATIC_URL'], settings['STATIC_ROOT'], settings['STATIC_HEADERS']
            ))

        if not settings['MEDIA_URL_IS_ON_OTHER_DOMAIN']:
            serve_static = True
            vassal_opts.extend(get_uwsgi_static_serving_opts(
                settings['MEDIA_URL'], settings['MEDIA_ROOT'], settings['MEDIA_HEADERS']
            ))

        if serve_static:
            vassal_opts.extend([
                'offload-threads = 2',  # Start 2 offloading threads for each worker
                'static-cache-paths = 86400',
                'static-cache-paths-name = staticpaths',
                'cache2 = name=staticpaths,items=5000,blocksize=1k,purge_lru,ignore_full',
                'static-gzip-all = true',  # Serve .gz files if that version is available
            ])

    return [
        'vassal-set = {}'.format(opt.replace(' = ', '=', 1))
        for opt in vassal_opts
    ]


def get_uwsgi_emperor_opts(settings, port):
    if settings['DATABASES']['default'].get('PASSWORD'):
        os.environ['DB_PASSWORD'] = settings['DATABASES']['default']['PASSWORD']
        pg_str = "pg://host={HOST} port={PORT} user={USER} password=$(DB_PASSWORD) dbname={NAME};{query}"
    else:
        pg_str = "pg://host={HOST} port={PORT} user={USER} dbname={NAME};{query}"

    return get_uwsgi_regular_opts(settings, port) + [
        'http = 0.0.0.0:{}'.format(port or settings.get('PORT')),
        'http-to = /tmp/fastrouter.sock',  # Fastrouter speaks the uwsgi protocol. We need to expose http via http-to
        'fastrouter = /tmp/fastrouter.sock',
        'fastrouter-use-code-string = 0:{}:get'.format(os.path.join(HERE, 'fastrouter_lookup.py')),
        'emperor = {}'.format(pg_str.format(query=VASSALS_SQL_QUERY, **settings['DATABASES']['default'])),
    ]


def assert_uwsgi_plugin_is_installed(plugin):
    # Simply call "uwsgi --need-plugins=<PLUGIN>" sounds tempting but does not work.
    # For some reason (maybe uwsgi inside virtualenv) the above wouldn't find the plugin even if it's installed.
    plugins = subprocess.check_output(['uwsgi --plugins-list; exit 0'], shell=True, stderr=subprocess.STDOUT)
    plugins = plugins.decode('utf-8').split('\n')
    plugins = plugins[:plugins.index('--- end of plugins list ---')]
    plugins = list(filter(lambda x: bool(x) and not(x.startswith('***')), plugins))
    plugins = [p.split()[-1] for p in plugins]
    assert plugin in plugins


def start_uwsgi_command(settings, port=None):
    def _create_working_dirs():
        for path in (conf.UWSGI_BASE_CONFIG_DIR, conf.UWSGI_BASE_SOCKETS_DIR):
            try:
                os.makedirs(path)
            except OSError:
                pass

    def _create_uwsgi_config_file(settings, port, uwsgi_config_file_path):
        # We can't use the regular ini writer because it does not allow repeating keys and does not keep order of keys
        ini = ['[uwsgi]']
        ini.extend(get_uwsgi_emperor_opts(settings, port))
        ini.extend(get_uwsgi_vassal_opts(settings, port))

        with open(uwsgi_config_file_path, 'w') as cfg_file:
            cfg_file.write('\n'.join(ini))

    uwsgi_config_file_path = os.path.join(conf.UWSGI_BASE_CONFIG_DIR, 'config.ini')

    # see 'required uwsgi plugins' in README for details about the uwsgi plugin
    assert_uwsgi_plugin_is_installed('emperor_pg')
    _create_working_dirs()
    _create_uwsgi_config_file(settings, port, uwsgi_config_file_path)

    return [
        'uwsgi',
        '--ini={}'.format(uwsgi_config_file_path)
    ]


if __name__ == '__main__':
    main()
