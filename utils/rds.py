import redis
from utils import config

pool = redis.ConnectionPool(host=config.get("redis.host"), port=config.get("redis.port"), db=config.get("redis.db"), password=config.get("redis.password"))
conn = redis.StrictRedis(connection_pool=pool)

conn.flushall()