import redis

pool = redis.ConnectionPool(host='192.168.88.132', port=6379, db=0, password="root")
conn = redis.StrictRedis(connection_pool=pool)