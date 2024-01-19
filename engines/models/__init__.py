self.play_order = 0
self.user_position = ['landlord_up', 'landlord', 'landlord_down'][self.user_position_code]


def step(self, position, action=None):
    if action is None:
        action = []
    win_rate = 0
    action_list = []
    if self.acting_player_position == position:
        if self.players2 is None:
            action, actions_confidence, action_list = self.players[1].act(self.game_infoset)
        else:
            if self.have_bomb(self.game_infoset.player_hand_cards):
                action, actions_confidence, action_list = self.players[1].act(self.game_infoset)
            else:
                action, actions_confidence, action_list = self.players2[1].act(self.game_infoset)
        win_rate = actions_confidence
        if win_rate < -0.05 and (30 in action and 20 in action or len(action) == 4 and len(set(action)) == 1):
            action = action_list[1][0]
        # 对直接出完情况做特判
        if len(action) != len(self.game_infoset.player_hand_cards):
            for l_action, l_score in action_list:
                if len(l_action) == len(self.game_infoset.player_hand_cards):
                    m_type = md.get_move_type(l_action)
                    if m_type["type"] not in [md.TYPE_14_4_22, md.TYPE_13_4_2]:
                        action = l_action
                        win_rate = 10000
                        print("检测到可直接出完出法")
            last_two_moves = self.get_last_two_moves()
            rival_move = None
            if last_two_moves[0]:
                rival_move = last_two_moves[0]
            elif last_two_moves[1]:
                rival_move = last_two_moves[1]
            if win_rate != 10000:
                path_list = []
                search_actions(self.game_infoset.player_hand_cards, self.game_infoset.other_hand_cards, path_list,
                               rival_move=rival_move)
                if len(path_list) > 0:
                    path = select_optimal_path(path_list)
                    if not check_42(path):
                        if action != path[0]:
                            print("检测到可直接出完路径:", self.action_to_str(action), "->", self.path_to_str(path))
                            action = path[0]
                            win_rate = 20000

    if len(action) > 0:
        self.last_pid = self.acting_player_position

    if action in bombs:
        self.bomb_num += 1

    self.last_move_dict[
        self.acting_player_position] = action.copy()

    self.card_play_action_seq.append((position, action))
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
    self.game_done()
    if not self.game_over:
        self.get_acting_player_position()
        self.game_infoset = self.get_infoset()
    # 返回动作和胜率,只有玩家角色会接受返回值
    action_message = {"action": str(''.join([EnvCard2RealCard[c] for c in action])),
                      "win_rate": float(win_rate)}
    action_list.sort(key=self.compare_action, reverse=True)
    show_action_list = [(str(''.join([EnvCard2RealCard[c] for c in action_info[0]])) if len(
        str(''.join([EnvCard2RealCard[c] for c in action_info[0]]))) > 0 else "Pass",
                         str(round(float(action_info[1]), 4))) for action_info in action_list]
    return action_message, show_action_list

while True:
    if self.play_order == 0:
        action_message, action_list = self.env.step(self.user_position)
        action_list = action_list[:8]
        action_list_str = "\n".join([ainfo[0] + " " + ainfo[1] for ainfo in action_list])
        winrate = action_list_str
        if first_run:
            self.initial_model_rate = round(float(action_message["win_rate"]), 3)  # win_rate at start
        first_run = False
        if action_message["action"] == "":
            pass
            # 不出
        else:
            if len(hand_cards_str) == 0 and len(action_message["action"]) == 1:
                pass
                # 出action_message["action"]
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