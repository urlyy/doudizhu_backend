import time

import socketio
from DO.room import Room
from utils.my_socket import sio
from utils import my_jwt, redis_key
from utils.rds import conn as redis
from DO.room_manager import RoomManager

namespace = "/game"


class GameSocket(socketio.AsyncNamespace):
    def __init__(self, namespace):
        super(GameSocket, self).__init__(namespace)

    async def emit_refresh(self, room_id, skip_sid=None):
        room_data = Room.get_by_id(room_id)
        await sio.emit('refresh', room_data, namespace=namespace, room=room_id, skip_sid=skip_sid)

    def get_ids(self, data):
        token = data["token"]
        user_id = my_jwt.get_user_id(token)
        room_id = redis.get(redis_key.player2room(user_id))
        if room_id:
            room_id = room_id.decode('utf-8')
        return user_id, room_id

    async def on_player_enter(self, sid, data):

        user_id, room_id = self.get_ids(data)
        print("进来了",user_id,room_id)
        if room_id:
            sio.enter_room(sid, room_id, namespace)
            print("推送回去了")
            await self.emit_refresh(room_id)
        else:
            await sio.emit('error', namespace=namespace, room=room_id)

    async def on_player_leave(self, sid, data):
        user_id, room_id = self.get_ids(data)
        if room_id:
            sio.leave_room(sid, room_id, namespace)
            Room.leave_player(room_id, user_id)
            if RoomManager.is_room_empty(room_id) or RoomManager.is_ai_room(room_id):
                RoomManager.rm_room(room_id)
            else:
                await self.emit_refresh(room_id)

    async def on_player_ready(self, sid, data):
        user_id, room_id = self.get_ids(data)
        Room.ready_player(room_id, user_id)
        await self.emit_refresh(room_id)

    async def on_player_ready_cancel(self, sid, data):
        user_id, room_id = self.get_ids(data)
        Room.ready_cancel_player(room_id, user_id)
        await self.emit_refresh(room_id)

    async def on_bid(self, sid, data):
        user_id, room_id = self.get_ids(data)
        score = int(data['score'])
        Room.bid(room_id, user_id, score)
        await self.emit_refresh(room_id)

    # 打出牌
    async def on_play_cards(self, sid, data):
        # 更新redis，把最新内容推送出去
        user_id, room_id = self.get_ids(data)
        played_cards = data['cards']
        res, game_end = Room.play_cards(room_id, user_id, played_cards)
        if game_end:
            print("游戏结束")
            room_data = Room.get_by_id(room_id)
            room_data['is_end']=True
            # 先让前端弹出弹窗
            await sio.emit('refresh', room_data, namespace=namespace, room=room_id)
            # 再结算数据，这里也需要修改room_data
            settlement_data = Room.settlement(room_id, room_data)
            await sio.emit('settlement', settlement_data, namespace=namespace, room=room_id)
            # 然后重置房间数据，但是保留玩家信息
            Room.init(room_id, room_data)
        else:
            await self.emit_refresh(room_id)

    async def on_ai_play_cards(self, sid, data):
        _, room_id = self.get_ids(data)
        idx = data['idx']
        Room.ai_play_cards(room_id, idx)
        # time.sleep(5)
        await self.emit_refresh(room_id)


    async def on_pass(self, sid, data):
        user_id, room_id = self.get_ids(data)
        Room.human_pass_cards(room_id)
        await self.emit_refresh(room_id)

    async def on_connect(self, sid, environ):
        # print("connect ", sid)
        pass

    def on_disconnect(self, sid):
        # print("disconnect ", sid)
        # print(sio.rooms(sio, namespace))
        pass
