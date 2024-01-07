from base import BaseModel
from peewee import CharField, IntegerField, ForeignKeyField
from user import User


class TableCloth(BaseModel):
    name = CharField(unique=True)
    desc = CharField(default="")
    price = IntegerField(default=2000)
    source = CharField()
    # 通过user.tweets进行查询
    user = ForeignKeyField(User, backref='tweets',column_name='user_id')
    class Meta:
        table_name="table_cloth"