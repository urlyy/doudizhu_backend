import socketio
from utils.my_socket import sio
from PO.chat_msg import ChatMsg as DB_ChatMsg
from PO.user import User as DB_User
from DO.chat_msg import ChatMsg
from jsonpickle import  encode,decode
namespace = "/chat"


class ChatSocket(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ):
        # print("connect ", sid)
        sql = DB_ChatMsg.select().limit(10).execute()
        data = list(sql)
        user_ids = set()
        for msg in data:
            user_id = msg.user_id
            user_ids.add(user_id)
        users = dict()
        for user_id in user_ids:
            db_user = DB_User.select().where(DB_User.id == user_id).first()
            users[user_id] = db_user
        res = []
        for db_msg in data:
            msg = ChatMsg.from_po(db_msg, users[db_msg.user_id])
            res.append(msg)
        await sio.emit("rcv_msgs", decode(encode(res, unpicklable=False)), namespace=namespace)

    async def on_send_msg(self, sid, data):
        text, user_id = data['text'], data['user_id']
        # print("message ", str(data))
        db_msg = DB_ChatMsg(text=text, user_id=user_id)
        db_msg.save()
        db_user = DB_User.select().where(DB_User.id == user_id).first()
        msg = [ChatMsg.from_po(db_msg, db_user)]
        await sio.emit("rcv_msgs", decode(encode(msg,unpicklable=False)), namespace=namespace)
        return True

    def on_disconnect(self, sid):
        # print("disconnect ", sid)
        pass
