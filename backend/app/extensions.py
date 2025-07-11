from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

import os

jwt = JWTManager()
if os.getenv("FLASK_ENV") == "production":
    socketio = SocketIO(cors_allowed_origins=["https://poker.soljt.ch", "https://www.poker.soljt.ch"], async_mode="eventlet")
else:
    socketio = SocketIO(cors_allowed_origins="*")