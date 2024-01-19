def start(self):
    # self.GameRecord.clear()
    # self.env.card_play_init(self.card_play_data_list)
    # cards_left = []
    # print("开始对局")
    # print("手牌:", self.user_hand_cards_real)
    # first_run = True
    # st = time.time()
    # step_count = 0
    while not self.env.game_over and self.RunGame:
        if self.play_order == 0:

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

            self.play_order = 2


        elif self.play_order == 2:
            if self.other_played_cards_real != "DX" or len(self.other_played_cards_real) == 4 and len(
                    set(self.other_played_cards_real)) == 1:
                self.handle_others(self.LPlayedCardsPos, self.LPlayedCard, "上家")
            else:
                self.other_played_cards_real = ""
                self.other_played_cards_env = ""
                self.env.step(self.user_position, [])
            self.GameRecord.append(self.other_played_cards_real if self.other_played_cards_real != "" else "Pass")
            self.play_order = 0


        step_count = (step_count + 1) % 3
        self.sleep(20)

    self.sleep(500)
    self.RunGame = False



def init_cards(self):
    self.RunGame = True
    GameHelper.Interrupt = False
    self.init_display()
    self.initial_model_rate = 0

    self.user_hand_cards_real = ""
    self.user_hand_cards_env = []
    self.other_played_cards_real = ""
    self.other_played_cards_env = []
    self.upper_played_cards_real = ""
    self.lower_played_cards_real = ""

    self.other_hand_cards = []

    self.three_landlord_cards_real = ""
    self.three_landlord_cards_env = []
    # 玩家角色代码：0-地主上家, 1-地主, 2-地主下家
    self.user_position_code = None
    self.user_position = ""

    self.card_play_data_list = {}

    self.play_order = 0

    self.env = None

    self.user_hand_cards_real = self.find_my_cards(self.MyHandCardsPos)
    self.UserHandCards.setText(self.user_hand_cards_real)
    self.user_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.user_hand_cards_real)]

    self.three_landlord_cards_real = self.find_three_landlord_cards(self.ThreeLandlordCardsPos)
    self.ThreeLandlordCards.setText("底牌：" + self.three_landlord_cards_real)
    self.three_landlord_cards_env = [RealCard2EnvCard[c] for c in list(self.three_landlord_cards_real)]
    for testCount in range(1, 5):
        if len(self.three_landlord_cards_env) > 3:
            self.ThreeLandlordCardsConfidence += 0.05
        elif len(self.three_landlord_cards_env) < 3:
            self.ThreeLandlordCardsConfidence -= 0.05
        else:
            break
        self.three_landlord_cards_real = self.find_three_landlord_cards(self.ThreeLandlordCardsPos)
        self.ThreeLandlordCards.setText("底牌：" + self.three_landlord_cards_real)
        self.three_landlord_cards_env = [RealCard2EnvCard[c] for c in list(self.three_landlord_cards_real)]

    self.user_position_code = self.find_landlord(self.LandlordFlagPos)
    try_count = 5
    while self.user_position_code is None and self.RunGame and try_count > 0:
        print("玩家角色获取失败！重试中…")
        try_count -= 1
        helper.LeftClick((900, 550))
        self.sleep(500)
        self.user_position_code = self.find_landlord(self.LandlordFlagPos)
    if self.user_position_code is None:
        return




    self.user_position = ['landlord_up', 'landlord', 'landlord_down'][self.user_position_code]
    for player in self.Players:
        player.setStyleSheet('background-color: rgba(255, 0, 0, 0);')
    self.Players[self.user_position_code].setStyleSheet('background-color: rgba(255, 0, 0, 0.1);')

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

    self.play_order = 0 if self.user_position == "landlord" else 1 if self.user_position == "landlord_up" else 2
    self.LastValidPlayPos = self.play_order

    ai_players = [self.user_position,
                  DeepAgent(self.user_position, self.card_play_model_path_dict[self.user_position])]
    # ai_players2 = [self.user_position,
    #                DeepAgent(self.user_position, self.card_play_wp_model_path[self.user_position])]
    self.env = GameEnv(ai_players, None)

    try:
        self.start()
    except Exception as e:
        print("运行时出现错误，已重置\n", repr(e))
        traceback.print_exc()
        self.stop()