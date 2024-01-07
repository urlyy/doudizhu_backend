import socketio
from utils.my_socket import sio

namespace = "/chat"


class ChatSocket(socketio.AsyncNamespace):
    def on_connect(self, sid, environ):
        # print("connect ", sid)
        pass


    async def on_send_msg(self, sid, data):
        text, user_id, username, avatar = data['text'], data['user_id'], data['username'], data['avatar']
        print("message ", str(data))
        await sio.emit("rcv_msg", data, namespace=namespace)
        return True

    def on_disconnect(self, sid):
        # print("disconnect ", sid)
        pass
