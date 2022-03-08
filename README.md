# django-multisite-plus

An extension to django-multisite and djangocms-multisite that brings:

* Packaging as an Addon for Divio Cloud and configuration of django-multisite
  and djangocms-multisite
* Tools to help handling moving database dumps between environments
  (live/stage/test/local) and still maintaining sensible domain names.
* single-process and multi-process deployment options

## Running the tests

Tests are run by tox and pytest. To run them, you need to have Docker, `tox`,
and `tox-docker` installed locally, they can be run simply by executing `tox`.


## Installation on Divio Cloud

Install the Addon.
To be able to use the multisite setup locally, define the
``DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT`` environment variable (and/or
set a value in the configuration form as a default).

```python
DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT='{}.192.168.99.100.xip.io'
```

This controls how you'll access the various sites. ``{}`` will be replaced with
the site slug. In the example above we're using ``xip.io`` a service that
returns the ip in the name for any domain following that format. Alternatively
you could create an entry in ``/etc/hosts`` for every domain you want to
support and point it to your local ip. Or have a local proxy that handles name
resolution.

The ``DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS`` environment variable controls
whether the domain names are re-written based on
``DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT`` on every app startup. Set it to
``True`` for local development and test servers. On the live server, when the
``real_domain`` should be used, set ``DJANGO_MULTISITE_PLUS_USE_REAL_DOMAIN``
to ``True``.

Now either create multiple Site entries (in admin under "Multisite+") and set
the slug and real domain accordingly (real domain can be blank). Or set the
``DJANGO_MULTISITE_PLUS_SITES`` in ``settings.py`` like this and make sure
``DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES`` is ``True``:

```python
DJANGO_MULTISITE_PLUS_SITES = {
    'portal': {
        'id': 1,
        'real_domain': 'www.example.com',
        'name': 'Example Portal',
    },
    'site1': {
        'id': 2,
        'real_domain': 'www.site1.com',
        'name': 'Site 1',
    },
    'site2': {
        'id': 3,
        'real_domain': 'www.site2.com',
        'name': 'Site 2',
    },
}
```

``id`` is the ``django.contrib.sites.Site.id`` and is **optional**. If left out
the slug (the key in the dict) will be used to create or update the existing
database entries. If present the site with the given id will be updated or
created.

## single-process vs multi-process

``DJANGO_MULTISITE_PLUS_MODE`` can be either ``single-process`` or
``multi-process``.

**``single-process``** means that only one python process will be run, which
will serve all domains. This makes requests slower (~400ms) because of some
reloading that needs to be done, but is much easier to deploy and does not use
much resources (ram). To accomplish this it uses the dynamic ``SITE_ID`` and
monkeypatches that come with ``django-multisite``.

**``multi-process``** means that there will be a process per ``SITE_ID``. The
setup uses a combination of
[uwsgi emperor mode](http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html)
(by reading domains directly from the postgres database from
``django.contrib.sites.Site``) and
[uwsgi fastrouter](http://uwsgi-docs.readthedocs.io/en/latest/Fastrouter.html)
to route incoming requests to the correct process. With the ``multi-process``
approach requests can be served faster, but it uses much more ram (multiplied
by the amount of sites).

## required uwsgi plugins

The ``multi-process`` mode requires the ``emperor_pg`` uwsgi plugin. It is
cumbersome to compile a custom version of uwsgi with this plugin, so we build
the default uwsgi wheel on the divio cloud with support already in there. At
the time of writing alpine is not supported yet. If this stops working, ask a
Divio Cloud SRE to update
https://wheels.aldryn.net/admin/wheelsproxy/package/59573/change/ . This is the
setup command we run on the wheels proxy before building the uwsgi wheel:

```
echo '[uwsgi]\nmain_plugin=python,gevent,emperor_pg\ninherit = base' >/tmp/profile.ini && export UWSGI_PROFILE=/tmp/profile.ini
```

## avoid slow requests on new workers

uwsgi will sometimes restart workers and start new workers on-the-fly. The
first request to a django process is really  slow though, because django loads
the bulk of its code at that time. This can produce slow requests at random
times. To avoid this we can load the bulk of the django app already at wsgi
init time. Replace ``wsgi.py`` with the following:

```python
import os
from aldryn_django import startup

application = startup.wsgi(path=os.path.dirname(__file__))

# Django loads most of its code when the first request comes in. But that
# means that the first request of a new worker will always be really
# slow. So we simulate a request here to warm the process up.
try:
    from django.test.client import Client
    client = Client()
    response = client.get('/', follow=True)
    print('Process warmed up with initial request.')
except Exception as exc:
    print('Failed to warm up process with initial request.')
```

## Multi-process tips

### Adding extra params to the vassals on a domain-level

Now the <Site> model can carry additional configurations to be used on
vassal/socket INI file. For example, one change the number of workers for a
given <Site> by simply:

```python
from django_multisite_plus.models import Site
site = Site.objects.get(id=XXXXX)
site.extra_uwsgi_ini = '''
workers = 5
'''
site.save()
```

Please note that those change will take effect only after a server restart.

## Future package structure

* Some of the features of django-multisite-plus may be worth merging into
  django-multisite.
* The configuration of djangocms-multisite could be moved to a separate Addon
  so this package does not need to depend on django-cms.
