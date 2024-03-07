def clean_query(sql):
    return " ".join([x.strip() for x in sql.strip().splitlines()])
