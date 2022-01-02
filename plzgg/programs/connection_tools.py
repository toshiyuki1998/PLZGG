from . import config
import psycopg2
def connect_db():
    connection = psycopg2.connect("host=10.0.2.10 dbname="+config.DB_NAME+" user="+config.DB_USERNAME+" password="+config.DB_PASSWORD)
    return connection