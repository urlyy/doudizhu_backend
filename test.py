import jsonpickle

from utils import redis_key
from utils.rds import conn as redis
from PO.user import User as DB_User
# room_id = "13311997418150793485035711961880786358"
# room_key = redis_key.room(room_id)


a = b"a"
print((str(a)))


# DB_User.update(rank=100).where(id == 3).execute()