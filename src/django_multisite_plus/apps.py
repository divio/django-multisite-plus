import django.apps


class AppConfig(django.apps.AppConfig):

    name = "django_multisite_plus"
    verbose_name = "Multisite+"

    def ready(self):
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured
        from django_multisite_plus import constants

        auto_populate_sites = getattr(
            settings, "DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES", None
        )
        if auto_populate_sites is True:
            raise ImproperlyConfigured(
                constants.AUTO_POPULATE_EXPLICITLY_ENABLED_ERROR_MESSAGE
            )
        elif auto_populate_sites is None:
            raise ImproperlyConfigured(
                constants.AUTO_POPULATE_DEFAULT_ENABLED_ERROR_MESSAGE
            )

        auto_rewrite_domains = getattr(
            settings, "DJANGO_MULTISITE_PLUS_AUTO_REWRITE_DOMAINS", None
        )
        if auto_rewrite_domains is True:
            raise ImproperlyConfigured(
                constants.AUTO_REWRITE_DOMAINS_EXPLICITLY_ENABLED_ERROR_MESSAGE
            )
        elif auto_rewrite_domains is None:
            rewrite_domains = getattr(
                settings, "DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS", True
            )
            if rewrite_domains:
                raise ImproperlyConfigured(
                    constants.AUTO_REWRITE_DOMAINS_NOT_DISABLED_ERROR_MESSAGE
                )
