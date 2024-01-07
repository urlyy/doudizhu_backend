import socketio


# mgr = socketio.AsyncRedisManager('redis://192.168.88.132:6379/0?password=root')
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*"
                           # ,client_manager=mgr
                           )