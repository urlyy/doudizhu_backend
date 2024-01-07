from fastapi import APIRouter, UploadFile
from main import app

router = APIRouter()

# 在子路由中定义路由
@router.get("/")
async def read_item():
    return {"message": "Hello from the subrouter"}

@router.get("/another")
async def read_another_item( file: UploadFile):
    return {"message": "Hello from another subrouter"}

# 将子路由注册到主应用
app.include_router(router, prefix="/shop", tags=["game"])