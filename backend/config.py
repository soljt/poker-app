import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(BASE_DIR, 'poker.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt")

    if os.getenv("FLASK_ENV") != "production":
        JWT_COOKIE_SECURE = False # DEBUG ONLY: set true when released
        JWT_COOKIE_SAMESITE = "Lax" # required for cookie inclusing in requests between diff domains
    else:
        JWT_COOKIE_SECURE = True # DEBUG ONLY: set true when released
        JWT_COOKIE_SAMESITE = "None" # required for cookie inclusing in requests between diff domains
    
    JWT_CSRF_IN_COOKIES = True # send the csrf token via cookie so that the frontend can grab from browser
    JWT_TOKEN_LOCATION = ["cookies"] # allows jwt in http-only cookie (protect against XSS attack)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    CACHE_REDIS_HOST = os.getenv("CACHE_REDIS_HOST", "localhost")
    CACHE_REDIS_PORT = int(os.getenv("CACHE_REDIS_PORT", 6379))
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_TYPE = "RedisCache"