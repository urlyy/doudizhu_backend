import json
from typing import List, Tuple

import jsonpickle

from utils import redis_key
from PO.user import User
from utils.rds import conn as redis
from utils import game_helper as gh
from DO.card import Card
from engines import czq
import copy

STATUS_WAITING = 0
STATUS_BID = 1
STATUS_PLAYING = 2


class Player:
    user_id: int
    idx: int
    rank: int
    is_ready: bool
    is_dizhu: bool
    cards: List[Card]

    def __init__(self, user_id, idx, rank):
        self.is_dizhu = False
        self.is_ready = False
        self.cards = []
        self.idx = idx
        self.user_id = user_id
        self.rank = rank

    @classmethod
    def generate(cls, user_id, idx, rank, is_ai=False):
        player = {
            "is_dizhu": False,
            "is_ready": is_ai,
            "cards": [],
            "idx": idx,
            "user_id": user_id,
            "rank": rank,
            "is_ai": is_ai
        }
        return player

    @classmethod
    def is_none(cls, p):
        return p == '{}'

    @classmethod
    def loads(cls, s: str) -> dict:
        return jsonpickle.decode(s)

    @classmethod
    def dumps(cls, d: dict) -> str:
        return jsonpickle.encode(d, unpicklable=False)


class Room:
    id: int
    players: List[Player]
    # 0正缺人 1人满 2正在进行
    status: int
    cur_player_idx: int
    dizhu_cards: List[Card] | str
    last_cards: List[Card]
    base_score: int
    multiple: int

    @classmethod
    def init_data(cls, id, is_ai=False):
        return {
            "id": id,
            "p-0": '{}',
            "p-1": '{}',
            "p-2": '{}',
            # "players": '[]',
            "status": STATUS_WAITING,
            "cur_player_idx": 0,
            "dizhu_cards": '[]',
            "last_cards": '[]',
            "base_score": 0,
            "multiple": 1,
            "last_cards_player_idx": -1,
            "is_ai": "True" if is_ai else "False"
        }

    @classmethod
    def init(cls, room_id, is_ai, prev_data=None):
        room_data = cls.init_data(room_id, is_ai)
        # TODO 清空未在线用户
        # 这里保留了上次的用户
        if prev_data != None:
            for i in range(3):
                p_key = f'p-{i}'
                prev_data['players'][i]['cards'] = []
                prev_data['players'][i]['is_ready'] = False
                prev_data['players'][i]['is_dizhu'] = False
                player = jsonpickle.encode(prev_data['players'][i], unpicklable=False)
                room_data[p_key] = player
        key = redis_key.room(room_id)
        redis.hset(key, mapping=room_data)

    @classmethod
    def players_iter(cls, room_key) -> Tuple[str, str, int] | None:
        for i in range(3):
            p_key = f"p-{i}"
            p = redis.hget(room_key, p_key).decode('utf-8')
            if Player.is_none(p):
                p = None
            yield p, p_key, i

    @classmethod
    def find_player_by_id(cls, room_key, user_id):
        for p, p_key, i in cls.players_iter(room_key):
            if p:
                player = jsonpickle.decode(p)
                if player['user_id'] == user_id:
                    return player, p_key, i
        return None

    @classmethod
    def __update_room_rank(cls, room_id):
        room_key = redis_key.room(room_id)
        sum_num = 0
        sum_rank = 0
        for p, p_key, i in cls.players_iter(room_key):
            if p:
                player = Player.loads(p)
                sum_rank += player['rank']
                sum_num += 1
        # 满人的时候不加入排名
        if sum_num == 3 or sum_num == 0:
            redis.zrem(redis_key.room_rank_sorted(), room_id)
        else:
            avg_rank = int(sum_rank / sum_num)
            redis.zadd(redis_key.room_rank_sorted(), {room_id: avg_rank})

    @classmethod
    def enter_player(cls, room_id, user_id, rank, ai_room=False):
        room_key = redis_key.room(room_id)
        idx = -1
        for p, p_key, i in cls.players_iter(room_key):
            if p is None:
                player = Player.generate(user_id, i, rank)
                redis.hset(room_key, p_key, json.dumps(player))
                idx = i
                break
        assert idx != -1
        if not ai_room:
            cls.__update_room_rank(room_id)
        redis.set(redis_key.player2room(user_id), room_id)

    @classmethod
    def enter_ai(cls, room_id):
        room_key = redis_key.room(room_id)
        for idx in [1, 2]:
            p_key = f"p-{idx}"
            ai_player = Player.generate(None, idx, None, True)
            redis.hset(room_key, p_key, json.dumps(ai_player))

    @classmethod
    def leave_player(cls, room_id, user_id):
        room_key = redis_key.room(room_id)
        res = cls.find_player_by_id(room_key, user_id)
        if res is not None:
            player, p_key, idx = res
            pipe = redis.pipeline()
            pipe.delete(redis_key.player2room(user_id))
            pipe.hset(room_key, p_key, "{}")
            pipe.execute()
            is_ai = redis.hget(room_key, "is_ai").decode("utf-8")
            if is_ai == "False":
                cls.__update_room_rank(room_id)

    @classmethod
    def ready_player(cls, room_id, user_id):
        room_key = redis_key.room(room_id)
        ready_cnt = 0
        for p, p_key, i in cls.players_iter(room_key):
            if p:
                player = jsonpickle.decode(p)
                if player['user_id'] == user_id:
                    player['is_ready'] = True
                    redis.hset(room_key, p_key, jsonpickle.encode(player, unpicklable=False))
                if player['is_ready'] == True:
                    ready_cnt += 1
        if ready_cnt == 3:
            cls.start(room_id)
            # 满三个了就启动

    @classmethod
    def start(cls, room_id):
        room_key = redis_key.room(room_id)
        redis.hset(room_key, 'status', STATUS_BID)
        # TODO先这样写
        # redis.hset(room_key, 'status', STATUS_PLAYING)
        # 发牌、生成地主牌
        cards_group = gh.game_init_cards()
        for p, p_key, i in cls.players_iter(room_key):
            player = jsonpickle.decode(p)
            player['cards']: list = cards_group[i]
            redis.hset(room_key, p_key, jsonpickle.encode(player, unpicklable=False))
        redis.hset(room_key, "dizhu_cards", jsonpickle.encode(cards_group[-1], unpicklable=False))

    @classmethod
    def ready_cancel_player(cls, room_id, user_id):
        room_key = redis_key.room(room_id)
        res = cls.find_player_by_id(room_key, user_id)
        if res:
            player, p_key, idx = res
            player['is_ready'] = False
            redis.hset(room_key, p_key, jsonpickle.encode(player, unpicklable=False))

    @classmethod
    def bid(cls, room_id, user_id, score):
        def set_dizhu(room_key, p_key):
            print(p_key)
            p = redis.hget(room_key, p_key)
            player = jsonpickle.decode(p)
            player['is_dizhu'] = True
            dizhu_cards = redis.hget(room_key, "dizhu_cards")
            dizhu_cards = jsonpickle.decode(dizhu_cards)
            player['cards'].extend(dizhu_cards)
            gh.sort_cards(player['cards'])
            redis.hset(room_key, 'status', STATUS_PLAYING)
            redis.hset(room_key, p_key, jsonpickle.encode(player, unpicklable=False))
            redis.hdel(room_key, 'tmp_bid_key')
            # 地主先出牌
            next_player_idx = p_key.split("-")[1]
            redis.hset(room_key, "cur_player_idx", next_player_idx)
            room_key = redis_key.room(room_id)
            # 如果是ai就开始构建环境
            print("daozhe")
            is_ai = redis.hget(room_key, "is_ai").decode("utf-8")
            print(is_ai)
            if is_ai == 'True':
                print(f"是ai房间:{is_ai}")
                czq.create_env(room_id)

        room_key = redis_key.room(room_id)
        p, p_key, idx = cls.find_player_by_id(room_key, user_id)
        cur_base_score = int(redis.hget(room_key, "base_score"))
        if score == 3:
            print("进来了啊")
            set_dizhu(room_key, p_key)
            return
        if score > cur_base_score:
            cur_base_score = score
            pipe = redis.pipeline()
            pipe.hset(room_key, "tmp_bid_key", p_key)
            pipe.hset(room_key, "base_score", cur_base_score)
            pipe.execute()
        if p_key == "p-2":
            if cur_base_score == 0:
                # 让第一个人当地主
                # 如果都不想当
                dizhu_key = "p-0"
            else:
                key: str = redis.hget(room_key, "tmp_bid_key").decode('utf-8')
                dizhu_key = key.split(":")[0]
            set_dizhu(room_key, dizhu_key)
        else:
            # 走下一个
            next_player_idx = str((int(p_key.split("-")[1]) + 1) % 3)
            redis.hset(room_key, "cur_player_idx", next_player_idx)

    @classmethod
    def __play_cards(cls, room_id, player, played_cards, player_idx) -> Tuple[bool, bool]:
        room_key = redis_key.room(room_id)
        # 删除该玩家手牌里的对应牌
        for played in played_cards:
            flag = -1
            for idx, card in enumerate(player['cards']):
                if played['suit'] == card['suit'] and played['number'] == card['number']:
                    flag = idx
                    break
            assert flag != -1
            player['cards'].pop(flag)
        # 并切换玩家
        cur_player_idx = redis.hget(room_key, 'cur_player_idx')
        next_player_idx_int = (int(cur_player_idx) + 1) % 3
        next_player_idx = str(next_player_idx_int)
        # 事务
        pipe = redis.pipeline()
        pipe.hset(room_key, f"p-{player_idx}", jsonpickle.encode(player, unpicklable=False))
        pipe.hset(room_key, 'last_cards', jsonpickle.encode(played_cards, unpicklable=False))
        pipe.hset(room_key, 'last_cards_player_idx', cur_player_idx)
        pipe.hset(room_key, 'cur_player_idx', next_player_idx)
        pipe.execute()
        if len(player['cards']) == 0:
            redis.hset(room_key, 'status', STATUS_WAITING)
            redis.hset(room_key,'cur_player_idx',"-1")
            return True, True
        return True, False

    @classmethod
    def ai_play_cards(cls, room_id, player_idx):
        print("ai的idx",player_idx)
        room_key = redis_key.room(room_id)
        ai_player = redis.hget(room_key, f"p-{player_idx}")
        ai_player = jsonpickle.decode(ai_player)
        # 从ai的结果获得真实需要打出的牌
        tmp_played_numbers: list = czq.ai_run(czq.global_envs[room_id])
        if len(tmp_played_numbers) == 0:
            cls.__pass_cards(room_id)
        else:
            real_cards = []
            tmp_cards: list = copy.deepcopy(ai_player['cards'])
            print("ai手牌")
            print(list(map(lambda item: item['number'], tmp_cards)))
            for number in tmp_played_numbers:
                flag = False
                for idx, c in enumerate(tmp_cards):
                    if c['number'] == number:
                        real_cards.append(tmp_cards.pop(idx))
                        flag = True
                        break
                assert flag
            return cls.__play_cards(room_id, ai_player, real_cards, player_idx)

    @classmethod
    def play_cards(cls, room_id, user_id, played_cards) -> Tuple[bool, bool]:
        room_key = redis_key.room(room_id)

        res = cls.find_player_by_id(room_key, user_id)
        assert res is not None
        player, p_key, player_idx = res
        # ai也要走一步
        is_ai = redis.hget(room_key, "is_ai").decode('utf-8')
        if is_ai == "True":
            czq.human_run(czq.global_envs[room_id], played_cards)
        return cls.__play_cards(room_id, player, played_cards, player_idx)


    @classmethod
    def __pass_cards(cls,room_id):
        room_key = redis_key.room(room_id)
        # 当前打出牌的前一个人
        cur_player_idx = redis.hget(room_key, 'cur_player_idx')
        next_player_idx = str((int(cur_player_idx) + 1) % 3)
        last_cards_player_idx = redis.hget(room_key, 'last_cards_player_idx').decode('utf-8')
        print(last_cards_player_idx, next_player_idx)
        # 将当前的人替换成刚pass的这个
        redis.hset(room_key, 'cur_player_idx', next_player_idx)
        # 如果一圈都打不起，打这张牌的人继续打
        if next_player_idx == last_cards_player_idx:
            redis.hset(room_key, 'last_cards', '[]')

    @classmethod
    def human_pass_cards(cls, room_id):
        is_ai = redis.hget(redis_key.room(room_id), "is_ai").decode('utf-8')
        if is_ai == "True":
            czq.human_run(czq.global_envs[room_id], [])
        cls.__pass_cards(room_id)

    @classmethod
    def settlement(cls, room_id, room_data) -> dict:
        # 除了计算还要修改redis里的数据
        room_key = redis_key.room(room_id)
        return {
            "player_data": [{"username": "czq", "avatar": "", "coin_diff": -100, "rank_diff": -100, "new_rank": 3100,
                             "new_coin": 180,
                             "is_di_zhu": True},
                            {"username": "qwer", "avatar": "", "coin_diff": -100, "rank_diff": -100, "new_rank": 2400,
                             "new_coin": 240,
                             "is_di_zhu": True},
                            {"username": "1234", "avatar": "", "coin_diff": -100, "rank_diff": -100, "new_rank": 1999,
                             "new_coin": 300,
                             "is_di_zhu": True}]
        }

    @classmethod
    def get_by_id(cls, room_id):
        key = redis_key.room(room_id)
        tmp = redis.hgetall(key)
        tmp_utf8 = {k.decode('utf-8'): v.decode('utf-8') for k, v in tmp.items()}
        players = []
        for i in range(3):
            key = f"p-{i}"
            p = tmp_utf8.pop(key)
            player: dict = jsonpickle.decode(p)
            cards = player.get("cards")
            if cards and isinstance(cards, str):
                player['cards'] = jsonpickle.decode(cards)
            players.append(player)
        tmp_utf8['players'] = players
        tmp_utf8['last_cards'] = jsonpickle.decode(tmp_utf8['last_cards'])
        # 叫分阶段不返回地主牌
        if int(tmp_utf8['status']) == STATUS_PLAYING:
            tmp_utf8['dizhu_cards'] = jsonpickle.decode(tmp_utf8['dizhu_cards'])
        else:
            tmp_utf8.pop('dizhu_cards')
        return tmp_utf8

    # # TODO 记得游戏结束要删除这个
    # @classmethod
    # def record_offline_player(cls, room_id, user_id):
    #     redis.hset(redis_key.offline_during_game(), user_id, room_id)
