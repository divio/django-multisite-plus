=========
Changelog
=========


Next version (unreleased)
=========================

* Add testing support via tox + docker/tox-docker + pytest.
* Move to ``src``-based project layout.
* Add initial compatibility with Django 2.2, 3.0, and 4.0.
* Add linting checks for isort and flake8.
* Move to PEP-517/PEP-518 distribution format.
* Use ``setuptools-scm`` for versioning.


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
