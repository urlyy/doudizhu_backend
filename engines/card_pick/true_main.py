
self.user_position = ['landlord_up', 'landlord', 'landlord_down'][self.user_position_code]
self.user_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.user_hand_cards_real)]

self.three_landlord_cards_real = self.find_three_landlord_cards(self.ThreeLandlordCardsPos)
self.ThreeLandlordCards.setText("底牌：" + self.three_landlord_cards_real)
self.three_landlord_cards_env = [RealCard2EnvCard[c] for c in list(self.three_landlord_cards_real)]
for i in set(AllEnvCard):
    self.other_hand_cards.extend([i] * (AllEnvCard.count(i) - self.user_hand_cards_env.count(i)))

self.card_play_data_list.update({
    'three_landlord_cards': self.three_landlord_cards_env,
    ['landlord_up', 'landlord', 'landlord_down'][(self.user_position_code + 0) % 3]:
        self.user_hand_cards_env,
    ['landlord_up', 'landlord', 'landlord_down'][(self.user_position_code + 1) % 3]:
        self.other_hand_cards[0:17] if (self.user_position_code + 1) % 3 != 1 else self.other_hand_cards[17:],
    ['landlord_up', 'landlord', 'landlord_down'][(self.user_position_code + 2) % 3]:
        self.other_hand_cards[0:17] if (self.user_position_code + 1) % 3 == 1 else self.other_hand_cards[17:]
})

# 正式开始前的抢牌加倍这些
def before_start(self):
    self.RunGame = True
    GameHelper.Interrupt = True
    have_bid = False
    is_taodou = False
    is_stolen = 0
    self.initial_multiply = 0
    self.initial_mingpai = 0
    self.initial_bid_rate = 0
    while self.RunGame:
        outterBreak = False
        jiaodizhu_btn = helper.LocateOnScreen("jiaodizhu_btn", region=(765, 663, 116, 50))
        qiangdizhu_btn = helper.LocateOnScreen("qiangdizhu_btn", region=(783, 663, 116, 50))
        jiabei_btn = helper.LocateOnScreen("jiabei_btn", region=self.GeneralBtnPos)
        self.detect_start_btn()
        print("等待加倍或叫地主", end="")
        while jiaodizhu_btn is None and qiangdizhu_btn is None and jiabei_btn is None and self.RunGame:
            self.detect_start_btn()
            print(".", end="")
            self.sleep(100)
            jiaodizhu_btn = helper.LocateOnScreen("jiaodizhu_btn", region=(765, 663, 116, 50))
            qiangdizhu_btn = helper.LocateOnScreen("qiangdizhu_btn", region=(783, 663, 116, 50))
            jiabei_btn = helper.LocateOnScreen("jiabei_btn", region=self.GeneralBtnPos)
        if jiabei_btn is None:
            img, _ = helper.Screenshot()
            cards, _ = helper.GetCards(img)
            cards_str = "".join([card[0] for card in cards])
            win_rate = BidModel.predict_score(cards_str)
            farmer_score = FarmerModel.predict(cards_str, "farmer")
            if not have_bid:
                with open("cardslog.txt", "a") as f:
                    f.write(str(int(time.time())) + " " + cards_str + " " + str(round(win_rate, 2)) + "\n")
            print("\n叫牌预估得分: " + str(round(win_rate, 3)) + " 不叫预估得分: " + str(round(farmer_score, 3)))
            self.BidWinrate.setText(
                "叫牌预估得分: " + str(round(win_rate, 3)) + " 不叫预估得分: " + str(round(farmer_score, 3)))
            self.sleep(10)
            self.initial_bid_rate = round(win_rate, 3)
            is_stolen = 0
            compare_winrate = win_rate
            if compare_winrate > 0:
                compare_winrate *= 2.5
            landlord_requirement = True
            if self.use_manual_landlord_requirements:
                landlord_requirement = manual_landlord_requirements(cards_str)

            if jiaodizhu_btn is not None:
                have_bid = True
                if win_rate > self.BidThresholds[0] and compare_winrate > farmer_score and landlord_requirement:
                    helper.ClickOnImage("jiaodizhu_btn", region=(765, 663, 116, 50), confidence=0.9)
                else:
                    helper.ClickOnImage("bujiao_btn", region=self.GeneralBtnPos)
            elif qiangdizhu_btn is not None:
                is_stolen = 1
                if have_bid:
                    threshold_index = 1
                else:
                    threshold_index = 2
                if win_rate > self.BidThresholds[
                    threshold_index] and compare_winrate > farmer_score and landlord_requirement:
                    helper.ClickOnImage("qiangdizhu_btn", region=(783, 663, 116, 50), confidence=0.9)
                else:
                    helper.ClickOnImage("buqiang_btn", region=self.GeneralBtnPos)
                have_bid = True
            else:
                pass
            if have_bid:
                result = helper.LocateOnScreen("taodouchang", region=(835, 439, 140, 40), confidence=0.9)
                if result is not None:
                    is_taodou = True
                    print("淘豆场，跳过加倍")
                    break
        else:
            llcards = self.find_three_landlord_cards(self.ThreeLandlordCardsPos)
            print("地主牌:", llcards)
            img, _ = helper.Screenshot()
            cards, _ = helper.GetCards(img)
            cards_str = "".join([card[0] for card in cards])
            self.initial_cards = cards_str
            if len(cards_str) == 20:
                # win_rate = LandlordModel.predict(cards_str)
                win_rate = LandlordModel.predict_by_model(cards_str, llcards)
                self.PreWinrate.setText("局前预估得分: " + str(round(win_rate, 3)))
                print("预估地主得分:", round(win_rate, 3))
            else:
                user_position_code = self.find_landlord(self.LandlordFlagPos)
                user_position = "up"
                while user_position_code is None:
                    user_position_code = self.find_landlord(self.LandlordFlagPos)
                    self.sleep(50)
                user_position = ['up', 'landlord', 'down'][user_position_code]
                self.landlord_position_code = user_position_code
                win_rate = FarmerModel.predict(cards_str, user_position)
                print("预估农民得分:", round(win_rate, 3))
                self.PreWinrate.setText("局前预估得分: " + str(round(win_rate, 3)))
            if len(cards_str) == 20:
                JiabeiThreshold = self.JiabeiThreshold[is_stolen]
            else:
                JiabeiThreshold = self.FarmerJiabeiThreshold

            print("等待其他人加倍……")
            self.sleep(3500)

            chaojijiabei_btn = helper.LocateOnScreen("chaojijiabei_btn", region=self.GeneralBtnPos, confidence=0.78)
            if chaojijiabei_btn is None and self.stop_when_no_chaojia:
                self.AutoPlay = False
                self.SwitchMode.setText("自动" if self.AutoPlay else "单局")
                self.sleep(10)
                print("检测到没有超级加倍卡，已停止自动模式")
            if win_rate > JiabeiThreshold[0]:
                chaojijiabei_btn = helper.LocateOnScreen("chaojijiabei_btn", region=self.GeneralBtnPos, confidence=0.78)
                if chaojijiabei_btn is not None:
                    helper.ClickOnImage("chaojijiabei_btn", region=self.GeneralBtnPos, confidence=0.78)
                    self.initial_multiply = 4
                else:
                    helper.ClickOnImage("jiabei_btn", region=self.GeneralBtnPos)
                    self.initial_multiply = 2
            elif win_rate > JiabeiThreshold[1]:
                helper.ClickOnImage("jiabei_btn", region=self.GeneralBtnPos)
                self.initial_multiply = 2
            else:
                helper.ClickOnImage("bujiabei_btn", region=self.GeneralBtnPos)
                self.initial_multiply = 1
            outterBreak = True
            break
        if outterBreak:
            break

    llcards = self.find_three_landlord_cards(self.ThreeLandlordCardsPos)
    wait_count = 0
    while len(llcards) != 3 and self.RunGame and wait_count < 15:
        print("等待地主牌", llcards)
        self.sleep(200)
        wait_count += 1
        llcards = self.find_three_landlord_cards(self.ThreeLandlordCardsPos)

    print("等待加倍环节结束")
    if not is_taodou:
        if len(cards_str) == 20:
            self.sleep(5000)
    else:
        self.sleep(3000)
    if win_rate > self.MingpaiThreshold:
        helper.ClickOnImage("mingpai_btn", region=self.GeneralBtnPos)
        self.initial_mingpai = 1
    print("结束")


def start(self):
    self.GameRecord.clear()
    self.env.card_play_init(self.card_play_data_list)
    cards_left = []
    print("开始对局")
    print("手牌:", self.user_hand_cards_real)
    first_run = True
    st = time.time()
    step_count = 0
    while not self.env.game_over and self.RunGame:
        if self.play_order == 0:
            self.PredictedCard.setText("...")
            action_message, action_list = self.env.step(self.user_position)
            self.UserHandCards.setText("手牌：" + str(''.join(
                [EnvCard2RealCard[c] for c in self.env.info_sets[self.user_position].player_hand_cards]))[::-1])
            action_list = action_list[:8]
            action_list_str = "\n".join([ainfo[0] + " " + ainfo[1] for ainfo in action_list])
            self.PredictedCard.setText(action_message["action"] if action_message["action"] else "不出")
            self.WinRate.setText(action_list_str)
            action_list_str = " | ".join([ainfo[0] + " " + ainfo[1] for ainfo in action_list])
            # self.sleep(400)
            hand_cards_str = ''.join(
                [EnvCard2RealCard[c] for c in self.env.info_sets[self.user_position].player_hand_cards])
            if first_run:
                self.initial_model_rate = round(float(action_message["win_rate"]), 3)  # win_rate at start
                first_run = False
            print("出牌:", action_message["action"] if action_message["action"] else "Pass", "| 得分:",
                  round(action_message["win_rate"], 3), "| 剩余手牌:", hand_cards_str)
            print(action_list_str)
            if not (self.upper_played_cards_real == "DX" or self.lower_played_cards_real == "DX" or
                    (len(hand_cards_str + action_message["action"]) == 1 and len(
                        self.upper_played_cards_real) > 1) or
                    (len(hand_cards_str + action_message["action"]) == 1 and len(
                        self.lower_played_cards_real) > 1)):
                if action_message["action"] == "":
                    tryCount = 2
                    result = helper.LocateOnScreen("pass_btn", region=self.PassBtnPos, confidence=0.85)
                    passSign = helper.LocateOnScreen("pass", region=(830, 655, 150, 70), confidence=0.85)
                    while result is None is None and tryCount > 0:
                        if not self.RunGame:
                            break
                        if passSign is not None and tryCount <= 0:
                            break
                        print("等待不出按钮")
                        self.detect_start_btn()
                        tryCount -= 1
                        result = helper.LocateOnScreen("pass_btn", region=self.PassBtnPos, confidence=0.85)
                        passSign = helper.LocateOnScreen("pass", region=(830, 655, 150, 70), confidence=0.85)
                        self.sleep(100)
                    helper.ClickOnImage("pass_btn", region=self.PassBtnPos, confidence=0.85)
                else:
                    if len(hand_cards_str) == 0 and len(action_message["action"]) == 1:
                        helper.SelectCards(action_message["action"], True)
                    else:
                        helper.SelectCards(action_message["action"])
                    tryCount = 10
                    result = helper.LocateOnScreen("play_card", region=self.PassBtnPos, confidence=0.85)
                    while result is None and tryCount > 0:
                        print("等待出牌按钮")
                        tryCount -= 1
                        result = helper.LocateOnScreen("play_card", region=self.PassBtnPos, confidence=0.85)
                        self.sleep(100)
                    self.sleep(100)
                    helper.ClickOnImage("play_card", region=self.PassBtnPos, confidence=0.85)
                self.sleep(300)
            else:
                print("要不起，跳过出牌")
            self.GameRecord.append(action_message["action"] if action_message["action"] != "" else "Pass")
            self.sleep(500)
            if action_message["action"]:
                cards = action_message["action"]
                move_type = get_move_type(self.real_to_env(cards))
                animation_types = {4, 5, 13, 14, 8, 9, 10, 11, 12}
                if move_type["type"] in animation_types or len(cards) >= 6:
                    self.waitUntilNoAnimation()

            self.detect_start_btn()

            self.play_order = 1

        elif self.play_order == 1:
            if self.other_played_cards_real != "DX" or len(self.other_played_cards_real) == 4 and len(
                    set(self.other_played_cards_real)) == 1:
                self.handle_others(self.RPlayedCardsPos, self.RPlayedCard, "下家")
            else:
                self.other_played_cards_real = ""
                self.other_played_cards_env = ""
                self.env.step(self.user_position, [])
            self.GameRecord.append(self.other_played_cards_real if self.other_played_cards_real != "" else "Pass")
            self.record_cards()
            self.play_order = 2
            self.sleep(200)

        elif self.play_order == 2:
            if self.other_played_cards_real != "DX" or len(self.other_played_cards_real) == 4 and len(
                    set(self.other_played_cards_real)) == 1:
                self.handle_others(self.LPlayedCardsPos, self.LPlayedCard, "上家")
            else:
                self.other_played_cards_real = ""
                self.other_played_cards_env = ""
                self.env.step(self.user_position, [])
            self.GameRecord.append(self.other_played_cards_real if self.other_played_cards_real != "" else "Pass")
            self.record_cards()
            self.play_order = 0
            self.sleep(100)
        step_count = (step_count + 1) % 3
        self.sleep(20)

    self.sleep(500)
    self.RunGame = False