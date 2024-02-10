from ai.bid import BidModel,FarmerModel

RealCard2EnvCard = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4,
                    '8': 5, '9': 6, 'T': 7, 'J': 8, 'Q': 9,
                    'K': 10, 'A': 11, '2': 12, 'X': 13, 'D': 14}
# 阈值
BidThresholds = [0,  # 叫地主阈值
                 0.03,  # 抢地主阈值 (自己第一个叫地主)
                 0.06]  # 抢地主阈值 (自己非第一个叫地主)


def transform_cards(cards):
    return list(map(lambda c: RealCard2EnvCard[c['number']], cards))


# 返回叫的分数
def bid(cards) -> int:
    tmp_cards = list(map(lambda c: c['number'], cards))
    win_rate = BidModel.predict_score(tmp_cards)
    farmer_score = FarmerModel.predict(tmp_cards, "farmer")
    # print(win_rate, farmer_score)
    compare_winrate = win_rate
    if compare_winrate > 0:
        #  源码是乘2.5
        compare_winrate *= 2.5
    # 牌差了，不叫
    if compare_winrate <= farmer_score:
        return 0
    # 一个一个看
    # 从大往小了看
    for score in range(1, 4, -1):
        idx = score - 1
        if win_rate > BidThresholds[idx]:
            return score
    return 0


# if __name__ == '__main__':
#     cards = "33445566778899JJJ"
#     cards = list(map(lambda c: {'number': c}, cards))
#     score = bid(cards)
#     print(score)