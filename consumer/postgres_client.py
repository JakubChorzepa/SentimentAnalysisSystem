import psycopg2
from psycopg2 import sql
from datetime import datetime 

class PostgresClient:
    def __init__(self, host, database, user, password, port):
        self.db_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.conn = None
    
    def _get_connection(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.db_params)
        return self.conn
        
    def _convert_to_timestamp(self, timestamp):
        try:
            return datetime.fromtimestamp(float(timestamp))
        except (TypeError, ValueError) as e:
            print(f"Error converting timestamp: {e}")
            return None
        
    def insert_post(self, post_data):
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            created_utc = self._convert_to_timestamp(post_data.get('created_utc'))
            
            insert_query = sql.SQL("""
                INSERT INTO mental_health_posts (id, title, text, created_utc, subreddit, sentiment_label, sentiment_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """)
            cursor.execute(insert_query, (
                post_data['id'],
                post_data.get('title', ''),
                post_data['text'],
                created_utc,
                post_data['subreddit'],
                post_data.get('label'),
                post_data.get('score')
            ))
            conn.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")
            if conn:
                conn.rollback()
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()