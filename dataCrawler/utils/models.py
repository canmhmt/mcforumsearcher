import psycopg2

def open_psql_connection():
    psql = connect_psql()
    cursor = psql.cursor()
    return psql, cursor
