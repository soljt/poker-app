from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import os

jwt = JWTManager()
if os.getenv("FLASK_ENV") == "production":
    socketio = SocketIO(cors_allowed_origins=["https://poker.soljt.ch", "https://www.poker.soljt.ch"], async_mode="eventlet")
else:
    socketio = SocketIO(cors_allowed_origins="*")

REDIS_PASSWORD = os.getenv("CACHE_REDIS_PASSWORD", "")
limiter = Limiter(key_func=get_remote_address, storage_uri=f"redis://:{REDIS_PASSWORD}@{os.getenv('CACHE_REDIS_HOST', 'localhost')}:{os.getenv('CACHE_REDIS_PORT', '6379')}")
cache = Cache()