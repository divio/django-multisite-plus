from django_multisite_plus import cli


def test_get_uwsgi_regular_opts():
    settings = {
        "DATABASES": {
            "default": {
                "HOST": "db-host",
                "PORT": 9999,
                "USER": "db-user",
                "PASSWORD": "db-pwd",
                "NAME": "db-name",
            }
        },
        "DJANGO_WEB_WORKERS": 2,
        "DJANGO_WEB_MAX_REQUESTS": 17,
        "DJANGO_WEB_TIMEOUT": 31,
    }

    opts = cli.get_uwsgi_regular_opts(settings, 1000)

    assert opts == [
        "module = wsgi",
        "master = true",
        "workers = 2",
        "max-requests = 17",
        "harakiri = 31",
        "lazy-apps = true",
        "honour-range = true",
        "enable-threads = true",
        "ignore-sigpipe = true",
        "ignore-write-errors = true",
        "disable-write-exception = true",
    ]
