from ai.play_cards.env.game import GameEnv
from ai.play_cards.evaluation.rlcard_agent import RLCardAgent
from ai.play_cards.evaluation.random_agent import RandomAgent
from ai.play_cards.evaluation.deep_agent import DeepAgent
from utils import redis_key
from utils.rds import conn as redis
from jsonpickle import decode
import os

EnvCard2RealCard = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
                    8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q',
                    13: 'K', 14: 'A', 17: '2', 20: 'X', 30: 'D'}

RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                    '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12,
                    'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30}


# 不同模型的玩家
def load_card_play_models():
    card_play_model_path_dict = {
        'landlord': os.path.join(os.getcwd(), "ai", "play_cards", "baselines", "douzero_ADP", "landlord.ckpt"),
        'landlord_up': os.path.join(os.getcwd(), "ai", "play_cards", "baselines", "sl", "landlord_up.ckpt"),
        'landlord_down': os.path.join(os.getcwd(), "ai", "play_cards", "baselines", "sl", "landlord_down.ckpt"), }
    players = {}
    for position in ['landlord', 'landlord_up', 'landlord_down']:
        if card_play_model_path_dict[position] == 'rlcard':
            players[position] = RLCardAgent(position)
        elif card_play_model_path_dict[position] == 'random':
            players[position] = RandomAgent()
        else:
            players[position] = DeepAgent(position, card_play_model_path_dict[position])
    return players


def step(self):
    action = self.players[self.acting_player_position].act(
        self.game_infoset)
    # print(self.acting_player_position, action)
    assert action in self.game_infoset.legal_actions

    if len(action) > 0:
        self.last_pid = self.acting_player_position

    # if action in bombs:
    #     self.bomb_num += 1

    self.last_move_dict[
        self.acting_player_position] = action.copy()

    self.card_play_action_seq.append(action)
    self.update_acting_player_hand_cards(action)

    self.played_cards[self.acting_player_position] += action

    if self.acting_player_position == 'landlord' and \
            len(action) > 0 and \
            len(self.three_landlord_cards) > 0:
        for card in action:
            if len(self.three_landlord_cards) > 0:
                if card in self.three_landlord_cards:
                    self.three_landlord_cards.remove(card)
            else:
                break


global_envs = dict()


def find_landlord(room_id):
    for idx in [0, 1, 2]:
        player = redis.hget(redis_key.room(room_id), f'p-{idx}')
        player = decode(player)
        if player['is_dizhu'] == True:
            return idx


def transform_cards(cards):
    return list(map(lambda c: RealCard2EnvCard[c['number']], cards))


def get_cards_info(room_id, landlord_idx):
    cards_info = dict()
    for idx in [0, 1, 2]:
        player = redis.hget(redis_key.room(room_id), f'p-{idx}')
        player = decode(player)
        cards = transform_cards(player['cards'])
        if idx == landlord_idx:
            cards_info['landlord'] = cards
        elif (landlord_idx + 1) % 3 == idx:
            cards_info['landlord_down'] = cards
        elif (landlord_idx + 2) % 3 == idx:
            cards_info['landlord_up'] = cards
    three_landlord_cards = redis.hget(redis_key.room(room_id), "dizhu_cards")
    three_landlord_cards = transform_cards(decode(three_landlord_cards))
    cards_info['three_landlord_cards'] = three_landlord_cards
    return cards_info


# 已经生成地主之后创建这个东西
def create_env(room_id):
    landlord_idx = find_landlord(room_id)
    cards_info = get_cards_info(room_id, landlord_idx)
    players = load_card_play_models()
    env = GameEnv(players)
    env.card_play_init(cards_info)
    print("放了一个env id",room_id)
    global_envs[room_id] = env


# 人只需要走，进行状态转移
# 注意如果传入空列表就是pass
def human_run(env: GameEnv, played_cards):
    cards = transform_cards(played_cards)
    print("当前角色:", env.acting_player_position)
    print("选项:",
          list(map(lambda cards: list(map(lambda c: EnvCard2RealCard[c], cards)), env.game_infoset.legal_actions)))
    # 排个序
    cards.sort()
    print("打出:", cards)
    env.step(cards)


# ai需要返回出的牌，让服务调用
# 我这里没写状态，因为是先地主后两个农民，所以这个状态算是让业务层维护
def ai_run(env:GameEnv):
    print("当前角色:", env.acting_player_position)
    print("选项",
          list(map(lambda cards: list(map(lambda c: EnvCard2RealCard[c], cards)), env.game_infoset.legal_actions)))
    played_cards = env.step()
    res = list(map(lambda c: EnvCard2RealCard[c], played_cards))
    # print("打出", res)
    return res
