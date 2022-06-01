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
