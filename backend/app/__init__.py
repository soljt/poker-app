import os
from flask import Flask
from flask_cors import CORS

if os.getenv("FLASK_ENV") == "production":
    import eventlet
    eventlet.monkey_patch()

from .extensions import jwt, socketio, limiter, cache
from app.db import init_db
from config import Config
from app.models.user import User
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app(config_class=Config, testing=False):
    app = Flask(__name__)
    # trust 1 proxy layer (NGINX) 
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    app.config.from_object(config_class)

    if testing:
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

    # initialize extensions
    # CORS
    origin_list = ["http://localhost:5173", "http://localhost", "http://localhost:80"]
    if os.getenv("FLASK_ENV") == "production":
        origin_list = ["https://poker.soljt.ch", "https://www.poker.soljt.ch"]
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": origin_list}})
    # db - see db.py
    init_db(app)
    # jwt (auth)
    jwt.init_app(app)
    # sockets (game state)
    socketio.init_app(app)
    # rate-limiting (leaderboard)
    limiter.init_app(app)
    cache.init_app(app)

    # import and register jwt handlers
    from app.auth import jwt_handlers
    app.after_request(jwt_handlers.refresh_expiring_jwts)

    # import and register socket event handlers
    from app import sockets

    # register blueprints
    from app.home import home as home_bp
    from app.auth import auth as auth_bp
    from app.util import util as util_bp
    from app.game import game as game_bp
    from app.admin import admin as admin_bp
    from app.leaderboard import leaderboard as leaderboard_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(util_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(leaderboard_bp)

    return app
