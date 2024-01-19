from peewee import CharField, IntegerField, ForeignKeyField
from .base import BaseModel

class ChatMsg(BaseModel):
    user_id = IntegerField()
    text = CharField()

    class Meta:
        table_name = "chat_msg"