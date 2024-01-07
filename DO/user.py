from PO.user import User as U
from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    coin: int
    rank: int
    avatar: str

    @staticmethod
    def from_bo(u: U):
        return User(u.id, u.username, u.coin, u.rank, u.avatar)

    def __init__(self, id: int, username: str, coin: int, rank: int, avatar: str):
        super().__init__(id=id, username=username, coin=coin, rank=rank, avatar=avatar)
