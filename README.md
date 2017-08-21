# django-multisite-plus

An extension to django-multisite that brings:

* Tools to help handling moving database dumps between environments
  (live/stage/test/local) and still maintaining sensible domain names.
* Packaging as an Addon for Divio Cloud and configuration of django-multisite and djangocms-multisite

## Installation on Divio Cloud

Install the Addon.
To be able to use the multisite setup locally, define the ``DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT``
environment variable (and/or set a value in the configuration form as a default).

```python
DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT='{}.192.168.99.100.xip.io'
```

This controls how you'll access the various sites. ``{}`` will be replaced with the site slug. In the example above
we're using ``xip.io`` a service that returns the ip in the name for any domain following that format.
Alternatively you could create an entry in ``/etc/hosts`` for every domain you want to support and point
it to your local ip. Or have a local proxy that handles name resolution.

The ``DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT`` environment variable controls whether the domain names
are re-written based on ``DJANGO_MULTISITE_PLUS_REWRITE_DOMAIN_FORMAT`` on every app startup. Set it to
``True`` for local development and test servers. Set it to ``False`` for the live server to use the real domains.

Now either create multiple Site entries (in admin under "Multisite+") and set the slug and real domain
accordingly (real domain can be blank).
Or set the ``DJANGO_MULTISITE_PLUS_SITES`` in ``settings.py`` like this and make sure ``DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES`` is ``True``:

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

``id`` is the ``django.contrib.sites.Site.id`` and is **optional**. If left out the slug will be used to
 create or update the existing database entries. If present the given site will be updated or created.

## Future package structure

* Some of the features of django-multisite-plus may be worth merged into django-multisite.
* The configuration of djangocms-multisite could be moved to a separate Addon so this package does not need to depend on django-cms.

