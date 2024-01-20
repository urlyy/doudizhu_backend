from utils import redis_key
from utils.rds import conn as redis

room_id = "13311997418150793485035711961880786358"
room_key = redis_key.room(room_id)
res = redis.exists(room_key)
print(res)