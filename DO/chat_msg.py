from PO.chat_msg import ChatMsg as DB_ChatMsg
from PO.user import User as DB_User

class ChatMsg:
    id: int
    user_id: int
    username: str
    avatar: str
    text: str
    rank: int
    create_time: str


    def __init__(self,id,text,create_time,user_id,username,avatar,rank):
        self.id = id
        self.text = text
        self.create_time = create_time
        self.username = username
        self.user_id = user_id
        self.avatar = avatar
        self.rank = rank

    @classmethod
    def from_po(cls, msg: DB_ChatMsg, user: DB_User):
        return cls(msg.id,msg.text,msg.create_time,
                   msg.user_id,user.username,user.avatar,user.rank)