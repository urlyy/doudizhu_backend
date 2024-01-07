from peewee import CharField, IntegerField, ForeignKeyField
from .base import BaseModel

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    coin = IntegerField(default=2000)
    rank = IntegerField(default=0)
    avatar = CharField(default="")

    class Meta:
        table_name = "user"