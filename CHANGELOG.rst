=========
Changelog
=========


0.7.2 (unreleased)
==================

* Add linting checks for ``isort`` and ``flake8``.
* Move to PEP-517/PEP-518 distribution format.
* Use ``setuptools-scm`` for versioning.
* Remove auto updating functionality on application startup. Users have to set
  ``DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES`` and ``DJANGO_MULTISITE_PLUS_AUTO_REWRITE_DOMAINS``
  to ``False`` in ``settings.py``, and use the ``multisite_plus_populate_sites``
  and ``multisite_plus_rewrite_domains`` management commands instead.


0.7.1 (2022-06-03)
==================

* Add testing support via tox + docker/tox-docker + pytest.
* Move to ``src``-based project layout.
* Add initial compatibility with Django 2.2, 3.0, and 4.0.


0.6.3 (2018-10-18)
==================

* Expose Site.name field in admin.


0.6.2 (2018-08-03)
==================

* Add multisite lib on addon.json.
* Prevent (meaningless) OSError from killing workers/vassals.


0.6.1 (2018-08-01)
==================

* Fix issues due to [filename length constraint on uwsgi](https://github.com/unbit/uwsgi/blob/master/core/socket.c#L178-L182).


0.6.0 (2018-02-20)
==================

* Add multi-process mode support.


0.1 (2017-06-19)
================

* Initial release.
