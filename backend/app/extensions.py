from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")