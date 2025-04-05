from flask import Blueprint

game = Blueprint('game', __name__, url_prefix="/game")

from app.game import routes