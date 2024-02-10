import BidModel
import FarmerModel



BidThresholds = [0,  # 叫地主阈值
                      0.3,  # 抢地主阈值 (自己第一个叫地主)
                      0]  # 抢地主阈值 (自己非第一个叫地主)
JiabeiThreshold = (
    (0.3, 0.15),  # 叫地主 超级加倍 加倍 阈值
    (0.5, 0.15)  # 叫地主 超级加倍 加倍 阈值  (在地主是抢来的情况下)
)


def bid(cards):
    cards = transform_cards(played_cards)
    cards_str = "333444569TTJJQKK2"
    win_rate = BidModel.predict_score(cards_str)
    farmer_score = FarmerModel.predict(cards_str, "farmer")

    print("\n叫牌预估得分: " + str(round(win_rate, 3)) + " 不叫预估得分: " + str(round(farmer_score, 3)))
    compare_winrate = win_rate
    if compare_winrate > 0:
        compare_winrate *= 2.5
    # 叫地主
    if win_rate > BidThresholds[0] and compare_winrate > farmer_score:
        # 叫
        pass
    else:
        # 不叫
        pass



# if jiabei_btn is None:
#     img, _ = helper.Screenshot()
#     cards, _ = helper.GetCards(img)
#     cards_str = "".join([card[0] for card in cards])
#     win_rate = BidModel.predict_score(cards_str)
#     farmer_score = FarmerModel.predict(cards_str, "farmer")
#     if not have_bid:
#         with open("cardslog.txt", "a") as f:
#             f.write(str(int(time.time())) + " " + cards_str + " " + str(round(win_rate, 2)) + "\n")
#     print("\n叫牌预估得分: " + str(round(win_rate, 3)) + " 不叫预估得分: " + str(round(farmer_score, 3)))
#     self.BidWinrate.setText(
#         "叫牌预估得分: " + str(round(win_rate, 3)) + " 不叫预估得分: " + str(round(farmer_score, 3)))
#     self.sleep(10)
#     self.initial_bid_rate = round(win_rate, 3)
#     is_stolen = 0
#     compare_winrate = win_rate
#     if compare_winrate > 0:
#         compare_winrate *= 2.5
#     landlord_requirement = True
#     if self.use_manual_landlord_requirements:
#         landlord_requirement = manual_landlord_requirements(cards_str)
#
#     if jiaodizhu_btn is not None:
#         have_bid = True
#         if win_rate > self.BidThresholds[0] and compare_winrate > farmer_score and landlord_requirement:
#             helper.ClickOnImage("jiaodizhu_btn", region=(765, 663, 116, 50), confidence=0.9)
#         else:
#             helper.ClickOnImage("bujiao_btn", region=self.GeneralBtnPos)
#     elif qiangdizhu_btn is not None:
#         is_stolen = 1
#         if have_bid:
#             threshold_index = 1
#         else:
#             threshold_index = 2
#         if win_rate > self.BidThresholds[
#             threshold_index] and compare_winrate > farmer_score and landlord_requirement:
#             helper.ClickOnImage("qiangdizhu_btn", region=(783, 663, 116, 50), confidence=0.9)
#         else:
#             helper.ClickOnImage("buqiang_btn", region=self.GeneralBtnPos)
#         have_bid = True
#     else:
#         pass
#     if have_bid:
#         result = helper.LocateOnScreen("taodouchang", region=(835, 439, 140, 40), confidence=0.9)
#         if result is not None:
#             is_taodou = True
#             print("淘豆场，跳过加倍")
#             break
# else:
#     llcards = self.find_three_landlord_cards(self.ThreeLandlordCardsPos)
#     print("地主牌:", llcards)
#     img, _ = helper.Screenshot()
#     cards, _ = helper.GetCards(img)
#     cards_str = "".join([card[0] for card in cards])
#     self.initial_cards = cards_str
#     if len(cards_str) == 20:
#         # win_rate = LandlordModel.predict(cards_str)
#         win_rate = LandlordModel.predict_by_model(cards_str, llcards)
#         self.PreWinrate.setText("局前预估得分: " + str(round(win_rate, 3)))
#         print("预估地主得分:", round(win_rate, 3))
#     else:
#         user_position_code = self.find_landlord(self.LandlordFlagPos)
#         user_position = "up"
#         while user_position_code is None:
#             user_position_code = self.find_landlord(self.LandlordFlagPos)
#             self.sleep(50)
#         user_position = ['up', 'landlord', 'down'][user_position_code]
#         self.landlord_position_code = user_position_code
#         win_rate = FarmerModel.predict(cards_str, user_position)
#         print("预估农民得分:", round(win_rate, 3))
#         self.PreWinrate.setText("局前预估得分: " + str(round(win_rate, 3)))
#     if len(cards_str) == 20:
#         JiabeiThreshold = self.JiabeiThreshold[is_stolen]
#     else:
#         JiabeiThreshold = self.FarmerJiabeiThreshold
#
#     print("等待其他人加倍……")
#     self.sleep(3500)
#
#     chaojijiabei_btn = helper.LocateOnScreen("chaojijiabei_btn", region=self.GeneralBtnPos, confidence=0.78)
#     if chaojijiabei_btn is None and self.stop_when_no_chaojia:
#         self.AutoPlay = False
#         self.SwitchMode.setText("自动" if self.AutoPlay else "单局")
#         self.sleep(10)
#         print("检测到没有超级加倍卡，已停止自动模式")
#     if win_rate > JiabeiThreshold[0]:
#         chaojijiabei_btn = helper.LocateOnScreen("chaojijiabei_btn", region=self.GeneralBtnPos, confidence=0.78)
#         if chaojijiabei_btn is not None:
#             helper.ClickOnImage("chaojijiabei_btn", region=self.GeneralBtnPos, confidence=0.78)
#             self.initial_multiply = 4
#         else:
#             helper.ClickOnImage("jiabei_btn", region=self.GeneralBtnPos)
#             self.initial_multiply = 2
#     elif win_rate > JiabeiThreshold[1]:
#         helper.ClickOnImage("jiabei_btn", region=self.GeneralBtnPos)
#         self.initial_multiply = 2
#     else:
#         helper.ClickOnImage("bujiabei_btn", region=self.GeneralBtnPos)
#         self.initial_multiply = 1
#     outterBreak = True
#     break