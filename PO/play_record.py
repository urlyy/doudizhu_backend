from peewee import CharField, IntegerField, ForeignKeyField,BooleanField
from .base import BaseModel

class PlayRecord(BaseModel):
    user_id = IntegerField()
    role = BooleanField()
    result = BooleanField()
    type = IntegerField()
    rank_diff =IntegerField()
    coin_diff = IntegerField()

    class Meta:
        table_name = "play_record"