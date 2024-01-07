from typing import Union

import jsonpickle
from fastapi import APIRouter
from fastapi.params import Form, Header
from DO.response import Response
from DO.user import User
from DO.room_manager import RoomManager
from DO.room import Room
from utils import my_jwt as jwt
from utils.my_socket import sio
from utils import redis_key
from utils.rds import conn as redis

router = APIRouter()


# 在子路由中定义路由
@router.get("/play")
async def search_room(rank: int, level: int, authorization: Union[str, None] = Header(None, convert_underscores=True)):
    user_id = jwt.get_user_id(authorization)
    room_id = redis.get(redis_key.player2room(user_id))
    # 中途返场
    if room_id != None:
        return Response.ok()
    else:
        # 新游戏
        room_id = RoomManager.match_room(user_id, rank, level)
        if room_id is None:
            return Response.fail()
        else:
            Room.enter_player(room_id, user_id, rank)
            return Response.ok()


# @router.post("/room/play")
# async def create_ai_room():
#     return Response.ok({"user": user.model_dump()})

@router.get("/{room_id}")
async def get_room_data(room_id: str, authorization: Union[str, None] = Header(None, convert_underscores=True)):
    # user_id = jwt.get_user_id(authorization)
    room_data = Room.get_by_id(room_id)
    return Response.ok(data={"room_data": room_data})

