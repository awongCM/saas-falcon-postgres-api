from dotenv import load_dotenv
import os

load_dotenv()

POSTGRESQL_DB = {
    'engine': 'postgresql+psycopg2',
    'username': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOSTNAME'),
    'db': os.getenv('POSTGRES_DB'),
}
