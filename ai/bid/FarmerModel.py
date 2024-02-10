# -*- coding: utf-8 -*-
# Created by: Vincentzyx
import os
import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.utils.data.dataset import Dataset
import time


def EnvToOnehot(cards):
    Env2IdxMap = {3:0,4:1,5:2,6:3,7:4,8:5,9:6,10:7,11:8,12:9,13:10,14:11,17:12,20:13,30:14}
    cards = [Env2IdxMap[i] for i in cards]
    Onehot = torch.zeros((4,15))
    for i in range(0, 15):
        Onehot[:cards.count(i),i] = 1
    return Onehot

def RealToOnehot(cards:list):
    RealCard2EnvCard = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4,
                        '8': 5, '9': 6, '10': 7, 'J': 8, 'Q': 9,
                        'K': 10, 'A': 11, '2': 12, 'X': 13, 'D': 14}
    cards = [RealCard2EnvCard[c] for c in cards]
    Onehot = torch.zeros((4,15))
    for i in range(0, 15):
        Onehot[:cards.count(i),i] = 1
    return Onehot


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        # input: 1 * 60
        self.conv1 = nn.Conv1d(1, 16, kernel_size=(3,), padding=1)  # 32 * 60
        self.dense1 = nn.Linear(1020, 1024)
        self.dense2 = nn.Linear(1024, 512)
        self.dense3 = nn.Linear(512, 256)
        self.dense4 = nn.Linear(256, 128)
        self.dense5 = nn.Linear(128, 1)

    def forward(self, xi):
        x = xi.unsqueeze(1)
        x = F.leaky_relu(self.conv1(x))
        x = x.flatten(1, 2)
        x = torch.cat((x, xi), 1)
        x = F.leaky_relu(self.dense1(x))
        x = F.leaky_relu(self.dense2(x))
        x = F.leaky_relu(self.dense3(x))
        x = F.leaky_relu(self.dense4(x))
        x = self.dense5(x)
        return x


Nets = {"up": Net(), "down": Net(), "farmer": Net()}
if os.path.exists("./landlord_up_weights_new.pkl"):
    if torch.cuda.is_available():
        Nets["up"].load_state_dict(torch.load("./landlord_up_weights_new.pkl"))
    else:
        Nets["up"].load_state_dict(torch.load("./landlord_up_weights_new.pkl", map_location=torch.device("cpu")))
    Nets["up"].eval()
if os.path.exists("./landlord_down_weights_new.pkl"):
    if torch.cuda.is_available():
        Nets["down"].load_state_dict(torch.load("./landlord_down_weights_new.pkl"))
    else:
        Nets["down"].load_state_dict(torch.load("./landlord_down_weights_new.pkl", map_location=torch.device("cpu")))
    Nets["down"].eval()
if os.path.exists("farmer_weights_new.pkl"):
    if torch.cuda.is_available():
        Nets["farmer"].load_state_dict(torch.load("farmer_weights_new.pkl"))
    else:
        Nets["farmer"].load_state_dict(torch.load("farmer_weights_new.pkl", map_location=torch.device("cpu")))
    Nets["farmer"].eval()


# 输出范围大概在 -0.6 ~ 3.45
def predict(cards, type="up"):
    net = Nets[type]
    x = torch.flatten(RealToOnehot(cards))
    x = x.unsqueeze(0)
    y = net(x)
    y = y.squeeze().item()
    return y

# if __name__ == "__main__":
#     print(predict("33334444555567", "up"))

# net = Nets['farmer']
# # 随机生成二进制输入数据（假设 batch_size 为 5）
# batch_size = 19999
# max_ones = 17
# # 生成一个形状为 (batch_size,  60) 的零张量
# input_data = torch.zeros((batch_size,  60))
# # 在每个样本中随机选择不超过 17 个位置，并将其设置为 1
# for i in range(batch_size):
#     ones_indices = torch.randperm(60)[:max_ones]
#     input_data[i, ones_indices] = 1
# # 正向传播
# output = net(input_data)
# # 打印输出的范围
# print("Output range:", output.min().item(), "-", output.max().item())