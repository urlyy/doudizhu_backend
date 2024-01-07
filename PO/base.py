from datetime import datetime

from peewee import PostgresqlDatabase, Model, CharField, IntegerField, ForeignKeyField, DateTimeField, AutoField
from playhouse.shortcuts import ReconnectMixin
from playhouse.pool import PooledPostgresqlDatabase

DB_NAME = 'czq'

#实现这个类可以避免崩溃
class ReconnectPostgresqlDatabase(ReconnectMixin, PooledPostgresqlDatabase):
    pass

db = ReconnectPostgresqlDatabase(DB_NAME, host="192.168.88.132",user='postgres', password='root')

class BaseModel(Model):
    create_time = DateTimeField(default=datetime.now, verbose_name="添加时间")
    id = AutoField(primary_key=True)
    class Meta:
        database = db