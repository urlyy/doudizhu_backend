import datetime
import jwt
import time
from utils import config

secret_key = config.get("jwt.secret")


def create_jwt(user_id: int) -> str:
    data = {
        # 公共声明
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),  # 过期时间
        'iat': datetime.datetime.utcnow(),  # 开始时间
        'iss': 'czq',  # (Issuer) 指明此token的签发者
        # 私有声明
        'data': {
            'user_id': user_id,
            'create_time': time.time()
        }
    }
    token = jwt.encode(data, secret_key, algorithm='HS256')
    return token


def get_payload(token: str, key=None) -> int | None:
    try:
        claim = jwt.decode(token, secret_key, issuer='czq', algorithms=['HS256'])
        payload = claim.get("data")
        if key:
            return payload.get(key)
        else:
            return payload
    except:
        return None


def get_user_id(token: str) -> int:
    return int(get_payload(token, "user_id"))
