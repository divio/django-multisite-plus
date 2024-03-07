from .utils import clean_query


# WARNING: ',' is more intuitive but doesn't work!
# uWSGI fails internally with ','.
UWSGI_ALIAS_SEPARATOR = "|"


# Below we use the domain hash in order to avoid filename length errors (uwsgi
# allows only 102 chars)
VASSALS_SQL_QUERY = clean_query(
    """
    SELECT
        MD5(ds.domain)||'.ini' ini_filename,
        CONCAT_WS(E'\\n',
            '[uwsgi]',
            'env = SITE_ID='||ds.id,
            'socket = {base_sockets_dir}'||MD5(ds.domain)||'.sock',
            ms.extra_uwsgi_ini
        ) ini_content,
        EXTRACT('epoch' from ms.last_updated_at) last_updated
    FROM
        django_multisite_plus_site AS ms
        INNER JOIN django_site as ds ON (ds.id = ms.site_id)
    WHERE
        ms.is_enabled = TRUE
    GROUP BY
        ds.id, ms.extra_uwsgi_ini, ms.last_updated_at;
    """
)


ALIAS_DOMAIN_MAPPING_QUERY = clean_query(
    """
    SELECT
        alias.domain AS origin_domain,
        site.domain AS destination_domain
    FROM
        multisite_alias AS alias
        INNER JOIN django_site AS site ON (alias.site_id = site.id)
    """
)


AUTO_POPULATE_EXPLICITLY_ENABLED_ERROR_MESSAGE = """
DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES cannot be True

You explicitly set the above setting to True and a configuration change is
necessary to proceed. This feature has been removed in a recent version of the
package because it was leading to race conditions when updating domains in
`multi-process` mode. You can now achieve the same effect by executing the
`multisite_plus_populate_sites` management command during deployment.
""".strip()


AUTO_POPULATE_DEFAULT_ENABLED_ERROR_MESSAGE = """
DJANGO_MULTISITE_PLUS_AUTO_POPULATE_SITES defaults to True

While the above setting has not been explicitly enabled, a previous version
of this package was automatically populating sites on startup and a
configuration change is necessary. This feature has been removed in a recent
version of the package because it was leading to race conditions when updating
domains in `multi-process` mode. You can now achieve the same effect by
executing the `multisite_plus_populate_sites` management command during
deployment.
""".strip()


AUTO_REWRITE_DOMAINS_EXPLICITLY_ENABLED_ERROR_MESSAGE = """
DJANGO_MULTISITE_PLUS_AUTO_REWRITE_DOMAINS cannot be True

You explicitly set the above setting to True and a configuration change is
necessary to proceed. This feature has been removed in a recent version of the
package because it was leading to race conditions when updating domains in
`multi-process` mode. You can now achieve the same effect by executing the
`multisite_plus_rewrite_domains` management command during deployment.
""".strip()


AUTO_REWRITE_DOMAINS_NOT_DISABLED_ERROR_MESSAGE = """
DJANGO_MULTISITE_PLUS_AUTO_REWRITE_DOMAINS is not False

While the above setting has not been explicitly enabled, it defaults to the
value of the DJANGO_MULTISITE_PLUS_REWRITE_DOMAINS setting, which is currently
set to True. This feature has been removed in a recent version of the package
because it was leading to race conditions when updating domains in
`multi-process` mode. You can now achieve the same effect by executing the
`multisite_plus_rewrite_domains` management command during deployment.
""".strip()
