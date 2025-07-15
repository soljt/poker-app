from flask import Blueprint

leaderboard = Blueprint('leaderboard', __name__, url_prefix="/leaderboard")

from app.leaderboard import routes