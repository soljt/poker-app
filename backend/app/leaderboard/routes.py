from flask import jsonify, request
from sqlalchemy import case
from app.db import db
from app.models.user import User
from app.extensions import limiter, cache
from app.leaderboard import leaderboard

@leaderboard.route("/")
@limiter.limit("10 per minute")
@cache.cached(timeout=10)
def fetch_leaderboard():
    balance = case(
        (User.username == 'kenna', User.chips - 10000),
        else_=User.chips - 5000
    )
    rows = db.session.execute(db.select(User.username, balance).order_by(balance.desc()).limit(10))
    users = [{"username": row[0],
              "balance": row[1]} for row in rows]
    return jsonify({
        "users": users,
    })