__all__=["upload","download","create_bucket","remove_object","create_presigned_url"]

import io
import os
import uuid
from datetime import timedelta

from minio import Minio
from pojo.entity import Bucket,FileObject

client = Minio('192.168.192.149:9000',
                        access_key='admin',
                        secret_key='admin123',
                        secure=False)

def upload(data:bytes,b:Bucket,o:FileObject,content_type)->bool:
    if not client.bucket_exists(b.name):
        create_bucket(b.name)
    stream = io.BytesIO(data)
    result = client.put_object(b.name, o.name, stream, length=len(data),content_type=content_type)
    return True

def create_bucket(bucket:str):
    client.make_bucket(bucket)

def download(bucket_name: str,object_name:str)->bytes|None:
    if not client.bucket_exists(bucket_name):
        return None
    try:
        response = client.get_object(bucket_name, object_name)
        return response.read()
    finally:
        response.close()
        response.release_conn()
    # return data
    # for d in data.stream(32 * 1024):
    #     yield from d


    # return StreamingResponse(download(), media_type="video/mp4")
    # path = "receive.img"
    # print(type(data.data))
    # with open(path, 'wb') as file_data:

    # return data.data

def create_presigned_url(b:Bucket,o:FileObject,days:int,hours:int,minutes:int)->str:
    url = client.get_presigned_url(
        "GET",
        b.name,
        o.name,
        expires=timedelta(days=days,hours=hours,minutes=minutes),
    )
    return url

def remove_object(b:Bucket,o:FileObject)->bool:
    client.remove_object(b.name, o.name)
    return True