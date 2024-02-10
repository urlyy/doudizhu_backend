import asyncio
import time

import socketio
from DO.room import Room, STATUS_WAITING
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
        return room_data

    def get_ids(self, data):
        token = data["token"]
        idx = data['idx']
        user_id = my_jwt.get_user_id(token)
        room_id = redis.get(redis_key.player2room(user_id))
        if room_id:
            room_id = room_id.decode('utf-8')
        cur_idx = redis.hget(redis_key.room(room_id), "cur_player_idx")
        if cur_idx:
            cur_idx = cur_idx.decode("utf-8")
        return user_id, room_id, cur_idx, idx

    async def on_player_enter(self, sid, data):
        user_id, room_id, _, _ = self.get_ids(data)
        if room_id:
            sio.enter_room(sid, room_id, namespace)
            # 返场
            if redis.exists(redis_key.player2room(user_id)) == 1:
                Room.back_player_during_play(room_id, user_id)
            await self.emit_refresh(room_id)
        else:
            await sio.emit('error', namespace=namespace, room=room_id)

    async def on_refresh(self, sid, data):
        _, room_id, _, _ = self.get_ids(data)
        room_data = await self.emit_refresh(room_id)
        print(room_data)

    async def on_player_leave_before_play(self, sid, data):
        user_id, room_id, _, idx = self.get_ids(data)
        print("before游戏开始离场", user_id, idx)
        if room_id:
            sio.leave_room(sid, room_id, namespace)
            Room.leave_player_before_play(room_id, user_id)
            if RoomManager.is_room_empty(room_id) or RoomManager.is_ai_room(room_id):
                RoomManager.rm_room(room_id)
            else:
                await self.emit_refresh(room_id)

    async def on_player_leave_during_play(self, sid, data):
        user_id, room_id, cur_idx, idx = self.get_ids(data)
        print("during游戏开始离场", user_id, idx)
        sio.leave_room(sid, room_id, namespace)
        Room.leave_player_during_play(room_id, user_id)
        if RoomManager.is_room_empty(room_id) or RoomManager.is_ai_room(room_id):
            RoomManager.rm_room(room_id)
        else:
            print(cur_idx == idx, cur_idx, idx, type(cur_idx), type(idx))
            if cur_idx == idx:
                cur_status = Room.get_status(room_id)
                if cur_status == 1:
                    await self.on_ai_bid(sid, data)
                else:
                    await self.on_ai_play_cards(sid, data)
            else:
                await self.emit_refresh(room_id)

    async def on_player_ready(self, sid, data):
        user_id, room_id, _, _ = self.get_ids(data)
        # print(user_id,idx)
        Room.ready_player(room_id, user_id)
        await self.emit_refresh(room_id)

    async def on_player_ready_cancel(self, sid, data):
        user_id, room_id, _, _ = self.get_ids(data)
        Room.ready_cancel_player(room_id, user_id)
        await self.emit_refresh(room_id)

    def is_next_tuoguan(self, room_id):
        step = redis.hget(redis_key.room(room_id), 'status')
        if step == STATUS_WAITING:
            return False
        is_tuoguan = Room.check_current(room_id)
        if is_tuoguan:
            return True
        return False

    async def on_bid(self, sid, data):
        user_id, room_id, cur_idx, _ = self.get_ids(data)
        score = int(data['score'])
        Room.bid(room_id, cur_idx, score)
        await self.emit_refresh(room_id)
        cur_status = Room.get_status(room_id)
        if self.is_next_tuoguan(room_id):
            # data['idx'] = (idx + 1) % 3
            if cur_status == 1:
                await self.on_ai_bid(sid, data)
            else:
                await self.on_ai_play_cards(sid, data)

    async def on_ai_bid(self, sid, data):
        user_id, room_id, cur_idx, _ = self.get_ids(data)
        Room.ai_bid(room_id, cur_idx)
        await self.emit_refresh(room_id)
        # print("ai_bid 下一个idx", cur_player_idx)
        cur_status = Room.get_status(room_id)
        # print("现在的状态",cur_status)
        # print(self.is_next_tuoguan(room_id))
        if self.is_next_tuoguan(room_id):
            # data['idx'] = (idx + 1) % 3
            loop = asyncio.get_event_loop()
            if cur_status == 1:
                async def tmp(sid, data):
                    time.sleep(1)
                    await self.on_ai_bid(sid, data)

                await loop.create_task(tmp(sid, data))
            else:
                # print("来打牌了")
                # await loop.create_task(self.on_ai_play_cards(sid, data))
                async def tmp(sid, data):
                    time.sleep(1)
                    await self.on_ai_play_cards(sid, data)

                await loop.create_task(tmp(sid, data))

    # 打出牌
    async def on_play_cards(self, sid, data):
        # 更新redis，把最新内容推送出去
        user_id, room_id, cur_idx, _ = self.get_ids(data)
        played_cards = data['cards']
        res, game_end = Room.play_cards(room_id, cur_idx, played_cards)
        if game_end:
            await self.handle_end(room_id)
        else:
            await self.emit_refresh(room_id)
            if self.is_next_tuoguan(room_id):
                # data['idx'] = (idx + 1) % 3
                loop = asyncio.get_event_loop()

                async def tmp(sid, data):
                    time.sleep(1)
                    await self.on_play_cards(sid, data)

                await loop.create_task(tmp(sid, data))

    async def handle_end(self, room_id):
        print("游戏结束")
        room_data = Room.get_by_id(room_id)
        room_data['is_end'] = True
        # 先让前端弹出弹窗
        await sio.emit('refresh', room_data, namespace=namespace, room=room_id)
        # 再结算数据，这里也需要修改room_data
        settlement_data = Room.settlement(room_id, room_data)
        await sio.emit('settlement', settlement_data, namespace=namespace, room=room_id)
        # 然后重置房间数据，但是保留玩家信息
        is_ai = room_data['is_ai'] == 'True'
        Room.init(room_id, is_ai, room_data)

    async def on_ai_play_cards(self, sid, data):
        _, room_id, cur_idx, _ = self.get_ids(data)
        # print("打牌了,现在的idx",idx)
        res, game_end = Room.ai_play_cards(room_id, cur_idx)
        if game_end:
            await self.handle_end(room_id)
        else:
            # time.sleep(3)
            await self.emit_refresh(room_id)
            loop = asyncio.get_event_loop()
            if self.is_next_tuoguan(room_id):
                async def tmp(sid, data):
                    time.sleep(1)
                    await self.on_ai_play_cards(sid, data)

                await loop.create_task(tmp(sid, data))

    async def on_pass(self, sid, data):
        user_id, room_id, cur_idx, idx = self.get_ids(data)
        Room.human_pass_cards(room_id)
        await self.emit_refresh(room_id)
        if self.is_next_tuoguan(room_id):
            # data['idx'] = (idx + 1) % 3
            loop = asyncio.get_event_loop()

            async def tmp(sid, data):
                time.sleep(3)
                await self.on_ai_play_cards(sid, data)

            await loop.create_task(tmp(sid, data))

    async def on_set_tuoguan(self, sid, data):
        user_id, room_id, cur_idx, idx = self.get_ids(data)
        new_tuoguan_status = data['is_tuoguan']
        is_my_term = cur_idx == str(idx)
        step = int(data['step'])
        Room.tuoguan_player(room_id, user_id, new_tuoguan_status)
        await self.emit_refresh(room_id)
        if is_my_term:
            loop = asyncio.get_event_loop()
            if step == 1:
                # print("托管，现在的idx", cur_player_idx)
                await loop.create_task(self.on_ai_bid(sid, data))
            elif step == 2:
                await loop.create_task(self.on_ai_play_cards(sid, data))
        # time.sleep(3)
        await self.emit_refresh(room_id)

    async def on_connect(self, sid, environ):
        # print("connect ", sid)
        pass

    def on_disconnect(self, sid):
        # print("disconnect ", sid)
        # print(sio.rooms(sio, namespace))
        pass
