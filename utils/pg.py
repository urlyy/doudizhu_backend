from peewee import PostgresqlDatabase
from utils import config

c = config.get("postgres")
db = PostgresqlDatabase(c['database'], host=c['host'],port=c['port'], user=c['user'], password=c['password'])