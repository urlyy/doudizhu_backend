import socketio
import uvicorn
from fastapi import FastAPI, applications
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from utils import config,my_socket

app =  None

def create_app():
    app = FastAPI(
        title="逗地主后端服务",
        version="1.0.0",
        description="全部接口",
        openapi_url="/api/api.json",
        docs_url="/docs"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    # 解决无法访问Swagger的问题
    def swagger_monkey_patch(*args, **kwargs):
        return get_swagger_ui_html(
            *args, **kwargs,
            swagger_js_url='https://cdn.bootcdn.net/ajax/libs/swagger-ui/4.10.3/swagger-ui-bundle.js',
            swagger_css_url='https://cdn.bootcdn.net/ajax/libs/swagger-ui/4.10.3/swagger-ui.css'
        )
    applications.get_swagger_ui_html = swagger_monkey_patch
    return app

def set_route(app: FastAPI, sio_app: socketio.ASGIApp):
    import controller
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.add_route("/socket.io/", route=sio_app, methods=["GET", "POST", "DELETE"])
    app.add_websocket_route("/socket.io/", sio_app)
    # 子路由
    app.include_router(controller.file.router, prefix="/file", tags=["file"])
    app.include_router(controller.user.router, prefix="/user", tags=["user"])
    app.include_router(controller.room.router, prefix="/room", tags=["room"])

def set_sio_route(sio: socketio.AsyncServer):
    from ws import game,chat
    sio.register_namespace(game.GameSocket(game.namespace))
    sio.register_namespace(chat.ChatSocket(chat.namespace))

if __name__ == '__main__':
    # 创建fastapi的服务和socketio的服务，并整合
    app = create_app()
    sio = my_socket.sio
    sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)
    # 集中设置两者的路由
    set_route(app,sio_asgi_app)
    set_sio_route(sio)
    # 启动服务
    print("qidong")
    uvicorn.run(app, host=config.get("server.host"), port=config.get("server.port")
                ,log_level='warning'
                )
