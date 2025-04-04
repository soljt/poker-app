import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'poker.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = "secret_sauce@45*"

    JWT_SECRET_KEY = "Bru5$j^yeah"
    JWT_COOKIE_SECURE = False # DEBUG ONLY: set true when released
    JWT_COOKIE_SAMESITE = "Lax" # required for cookie inclusing in requests between diff domains
    JWT_CSRF_IN_COOKIES = True # send the csrf token via cookie so that the frontend can grab from browser
    JWT_TOKEN_LOCATION = ["cookies"] # allows jwt in http-only cookie (protect against XSS attack)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)