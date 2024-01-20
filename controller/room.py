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


@router.get("/play/{room_id}")
async def search_room_by_id(room_id,rank: int, authorization: Union[str, None] = Header(None, convert_underscores=True)):
    user_id = jwt.get_user_id(authorization)
    user_room_id = redis.get(redis_key.player2room(user_id))
    # 中途返场
    if user_room_id != None:
        return Response.fail(message="您上一把还没结束")
    else:
        # 首先看有没有房间
        exist = RoomManager.room_exist(room_id)
        if exist:
            is_full = RoomManager.is_room_full(room_id)
            if not is_full:
                Room.enter_player(room_id, user_id, rank)
                return Response.ok()
        return Response.fail(message="房间不存在或房间已满")


@router.get("/play/ai")
async def create_ai_room(rank: int, authorization: Union[str, None] = Header(None, convert_underscores=True)):
    user_id = jwt.get_user_id(authorization)
    room_id = RoomManager.create_room(True)
    Room.enter_ai(room_id)
    Room.enter_player(room_id, user_id, rank, True)
    return Response.ok()


@router.get("/{room_id}")
async def get_room_data(room_id: str, authorization: Union[str, None] = Header(None, convert_underscores=True)):
    # user_id = jwt.get_user_id(authorization)
    room_data = Room.get_by_id(room_id)
    return Response.ok(data={"room_data": room_data})