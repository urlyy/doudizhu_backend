import uuid

import jsonpickle

from utils.rds import conn as redis
from DO.room import Room
from utils import redis_key
from ai.play_cards import global_envs


class RoomManager:
    @classmethod
    def create_room(cls, is_ai=False):
        room_id = str(uuid.uuid4().int)[:]
        Room.init(room_id, is_ai)
        return room_id

    # 为用户匹配，只返回目标房间id，不进行进入操作
    # 用户匹配失败后，前端每隔5秒请求匹配房间
    # 前端会慢慢累加level
    # 保持纯函数
    @classmethod
    def match_room(cls, user_id: int, rank: int, level: int) -> str | None:
        room_num = redis.zcard(redis_key.room_rank_sorted())
        # 段位差太远了，直接开新房间
        if level == 10 or room_num == None or room_num == 0:
            room_id = cls.create_room()
            return room_id
        # 正常匹配
        match_range = (rank - level * 200, rank + level * 200)
        room_ids = redis.zrangebyscore(redis_key.room_rank_sorted(), match_range[0], match_range[1], withscores=False)
        # 遍历所有房间
        if len(room_ids) > 0:
            return room_ids[0].decode('utf-8')
        else:
            return None

    @classmethod
    def is_room_empty(cls, room_id):
        room_key = redis_key.room(room_id)
        # 人数不够就删除房间
        cnt = 0
        for p, p_key, i in Room.players_iter(room_key):
            if p:
                cnt += 1
                player = jsonpickle.decode(p)
                if player['is_withdraw'] == True:
                    cnt-=1
        return cnt == 0

    @classmethod
    def room_exist(cls, room_id):
        room_key = redis_key.room(room_id)
        return redis.exists(room_key) == 1

    @classmethod
    def is_ai_room(cls, room_id):
        room_key = redis_key.room(room_id)
        return redis.hget(room_key, "is_ai").decode("utf-8") == "True"

    @classmethod
    def is_room_full(cls, room_id):
        room_key = redis_key.room(room_id)
        # 人数不够就删除房间
        cnt = 0
        for p, p_key, i in Room.players_iter(room_key):
            if p:
                cnt += 1
        return cnt == 3

    @classmethod
    def rm_room(cls, room_id):
        room_key = redis_key.room(room_id)
        room_sorted_key = redis_key.room_rank_sorted()
        pipe = redis.pipeline()
        pipe.delete(room_key)
        pipe.zrem(room_sorted_key, room_id)
        # 删玩家
        for p_str, p_key, i in Room.players_iter(room_key):
            if p_str:
                player = jsonpickle.decode(p_str)
                user_id = player['user_id']
                pipe.delete(redis_key.player2room(user_id))
        pipe.execute()
        if room_id in global_envs.keys():
            global_envs.pop(room_id)

# class Player(BaseModel):
#     name: str
#     coin: int
#
#     def __init__(self, name, coin):
#         super().__init__(name=name, coin=coin)
#
#
# class Room(BaseModel):
#     id: int
#     players: List[Player]
#


# p1 = Player("urlly", 1)
# p2 = Player("lyy", 30)
# room = {"id": 1, "players": [p1, p2]}
# room['players'] = json.dumps([p.model_dump_json() for p in room['players']])
# key = f"room:{1}"
# # redis.hset(key, mapping=room)
# data = redis.hgetall(key)
# data = {k.decode('utf-8'): v.decode('utf-8') for k,v in data.items()}
# data['players'] = [json.loads(p) for p in json.loads(data['players'])]
# room = Room(**data)
# print(room)
# s = json.dumps([r.model_dump_json() for r in room['players']])


# key = f"room:{1}"
# redis.hset(key, mapping=room)

# class RoomManager:
#     @staticmethod
#     def add_room(room_id, room):
#         """
#         保存房间对象到 Redis Hash
#         """
#         key = f"room:{room_id}"
#         redis.hset(key, mapping=room_data)
#
#     def get_room(self, room_number):
#         """
#         获取房间对象
#         """
#         key = f"room:{room_number}"
#         room_data = self.redis_client.hgetall(key)
#         if room_data:
#             # 将字节转换为字符串
#             room_data = {k.decode("utf-8"): v.decode("utf-8") for k, v in room_data.items()}
#             return room_data
#         else:
#             return None
#
#     def get_room_field_value(self, room_number, field):
#         """
#         通过字段获取房间对象的值
#         """
#         key = f"room:{room_number}"
#         value = self.redis_client.hget(key, field)
#         if value:
#             return value.decode("utf-8")
#         else:
#             return None
#
#
# # 示例用法
# room_manager = RoomManager(redis_client)
#
# # 保存房间对象到 Redis Hash
# room_data = {"name": "Room 12345", "capacity": "10"}
# room_manager.save_room("12345", room_data)
#
# # 获取整个房间对象
# room_obj = room_manager.get_room("12345")
# print(room_obj)
#
# # 获取房间对象的特定字段值
# room_capacity = room_manager.get_room_field_value("12345", "capacity")
# print(room_capacity)
