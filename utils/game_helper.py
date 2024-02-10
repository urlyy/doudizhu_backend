import uuid
from typing import List

from DO.card import Card
from random import randint


def card2code(number: str) -> int:
    RealCard2EnvCard = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4,
                        '8': 5, '9': 6, '10': 7, 'J': 8, 'Q': 9,
                        'K': 10, 'A': 11, '2': 12, 'X': 13, 'D': 14}
    return RealCard2EnvCard[number]


# 原地排序
def sort_cards(cards: List[Card] | List[dict]):
    if len(cards) == 0:
        return
    if isinstance(cards[0], dict):
        cards.sort(key=lambda c: card2code(c['number']), reverse=True)
    elif isinstance(cards[0], Card):
        cards.sort(key=lambda c: card2code(c.number), reverse=True)


def game_init_cards():
    def init_cards() -> List[Card]:
        suits = "♠♣♦♥"
        cards = []
        for s in suits:
            for i in range(2, 11):
                cards.append(Card(str(i), s))
            cards.append(Card("A", s))
            cards.append(Card("J", s))
            cards.append(Card("Q", s))
            cards.append(Card("K", s))
        # 'D'王和'X'王
        cards.append(Card("D"))
        cards.append(Card("X"))
        return cards

    # 用剩下的牌随机出来17张牌
    def random_hand_cards(remaining_cards: List[Card]) -> List[Card]:
        cards = []
        for _ in range(17):
            idx = randint(1, len(remaining_cards) - 1)
            # 测试用
            # idx = 0
            cards.append(remaining_cards[idx])
            remaining_cards.pop(idx)
        return cards

    cards = init_cards()
    p0 = random_hand_cards(cards)
    p1 = random_hand_cards(cards)
    p2 = random_hand_cards(cards)
    sort_cards(p0)
    sort_cards(p1)
    sort_cards(p2)
    return [p0, p1, p2, cards]


def generate_room_id():
    room_id = str(uuid.uuid4().int)[:]  # 取 UUID 的前 8 位作为房间号
    return room_id
    # ids = set()
    # cnt = 0
    # for i in range(100000000):
    #     id = generate_room_id()
    #     if id in ids:
    #         print(i, id)
    #         cnt += 1
    #         print("碰撞了噢")
    #     else:
    #         ids.add(id)
    # print(cnt)


# 返回金币/排名的差值
def settlement(base_score: int, multiple: int, is_dizhu: bool, is_winner: bool, withdraw: bool = False):
    base_coin_diff = 100
    coin_diff = base_score * multiple
    rank_diff = 30
    if not is_winner:
        coin_diff = -coin_diff
        rank_diff = -30
    if is_dizhu:
        coin_diff *= 2
        rank_diff *= 2
    if withdraw:
        coin_diff = -abs(coin_diff * 3)
        rank_diff = -abs(rank_diff * 3)
    return coin_diff * base_coin_diff, rank_diff
