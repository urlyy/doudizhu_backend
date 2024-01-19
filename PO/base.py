from datetime import datetime

from peewee import PostgresqlDatabase, Model, CharField, IntegerField, ForeignKeyField, DateTimeField, AutoField
from playhouse.shortcuts import ReconnectMixin
from playhouse.pool import PooledPostgresqlDatabase

from utils import config

c = config.get("postgres")
#实现这个类可以避免崩溃
class ReconnectPostgresqlDatabase(ReconnectMixin, PooledPostgresqlDatabase):
    pass

db = ReconnectPostgresqlDatabase(c['database'], host=c['host'],user=c['user'], password=c['password'])

class BaseModel(Model):
    create_time = DateTimeField(default=datetime.now, verbose_name="添加时间")
    id = AutoField(primary_key=True)
    class Meta:
        database = db