import uuid
from fastapi import APIRouter, UploadFile
from DO.response import Response
from utils import config
import os


router = APIRouter()

@router.post("/")
def upload(file: UploadFile):
    # 生成随机新文件名
    file_name, file_extension = os.path.splitext(file.filename)
    new_uuid = str(uuid.uuid4())
    new_filename = f"{new_uuid}{file_extension}"
    static_dir = config.get('server.static_dir')
    relative_path = os.path.join(static_dir, new_filename)
    # 将文件写入本地
    with open(os.path.join(os.getcwd(), relative_path), "wb") as new_file:
        new_file.write(file.file.read())
    if True:
        url = f"http://{config.get('server.host')}:{config.get('server.port')}/{static_dir}/{new_filename}"
        return Response.ok({"file": url})
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    # 如果条件不满足，可以使用 HTTPException 抛出自定义状态码

