from datetime import datetime, timedelta, timezone
from flask import Flask, request, session, jsonify
from flask_cors import CORS
from .extensions import jwt, socketio
from flask_jwt_extended import create_access_token, current_user, decode_token, get_csrf_token, get_jwt, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.game_logic.game_logic import PokerRound, Player
from app.db import init_db, db
from app.models.user import User
from sqlalchemy.exc import IntegrityError
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # initialize extensions
    # CORS
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})
    # db - see db.py
    init_db(app)
    # jwt (auth)
    jwt.init_app(app)
    # sockets (game state)
    socketio.init_app(app)

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
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(util_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(admin_bp)

    return app

############################# AUTHENTICATION ##########################################

######################### UTIL METHODS ######################################

# with app.test_request_context():
#     print(url_for('hello_world'))
#     print(url_for('hello_you', name='John Doe'))
