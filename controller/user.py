from typing import Union

from fastapi import APIRouter, HTTPException
from fastapi.params import Form, Header
from DO.response import Response
from DO.user import User
from PO.user import User as DB_User
from utils import my_jwt

router = APIRouter()


# 在子路由中定义路由
@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    db_user = DB_User.select().where(DB_User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="不存在该用户")
    token = my_jwt.create_jwt(db_user.id)
    user = User.from_bo(db_user)
    return Response.ok({"user": user.model_dump(), "token": token})


# 在子路由中定义路由
@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    db_user = DB_User.select().where(DB_User.username == username).first()
    if db_user is not None:
        return Response.fail(message="该用户名已被占用")
    db_user = DB_User(username=username, password=password)
    db_user.save()
    return Response.ok()


@router.get("/{user_id}")
async def get_profile(user_id: int):
    db_user = DB_User.select().where(DB_User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="不存在该用户")
    user = User.from_bo(db_user)
    return Response.ok({"user": user.model_dump()})


@router.post("/avatar")
async def update_avatar(avatar: str, authorization: Union[str, None] = Header(None)):
    my_id = my_jwt.get_user_id(authorization)
    DB_User.update(avatar=avatar).where(DB_User.id == my_id).execute()
    return Response.ok()
