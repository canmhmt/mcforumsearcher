import psycopg2
import traceback
from contextlib import contextmanager
from utils.connectDB import connect_psql

# For PSQL connections (open, close connection)
@contextmanager
def psql_cursor():
    conn = None
    cursor = None
    try:
        conn = connect_psql()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except:
        if conn:
            conn.rollback()
        traceback.print_exc()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# For PSQL Queries
class PsqlQuery():
    @staticmethod
    def get_active_forums_query():
        try:
            with psql_cursor() as cursor:
                cursor.execute("""
                SELECT forum_name_slug, base_topic_url FROM mcforumsearcher.public.forums WHERE is_active = 1;
                """)
                fetched_data = cursor.fetchall()
                if fetched_data:
                    parsed_data = [data[0] for data in fetched_data]
                    return True, parsed_data
                return False, [] 
        except:
            traceback.print_exc()
            return False, [] 

