from flask_jwt_extended import current_user, jwt_required
from functools import wraps
from flask import abort, jsonify, request
from app.admin import admin
from app.db import db
from app.models.user import RoleEnum, User
from sqlite3 import IntegrityError


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != RoleEnum.admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    page = int(request.args.get("page", 1))
    per_page = 10

    pagination = db.paginate(db.select(User).order_by(User.username), page=page, per_page=per_page, error_out=False)
    return jsonify({
        "users": [u.to_dict() for u in pagination.items],
        "totalPages": pagination.pages,
        "currentPage": pagination.page,
    })

@admin.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_user(user_id):
    data = request.json
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
    if not user:
        abort(404)

    if "chips" in data:
        user.chips = data["chips"]
    if "role" in data:
        user.role = data["role"]

    db.session.commit()
    return jsonify(user.to_dict())

@admin.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
    if not user:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    return '', 204

@admin.route("/users", methods=["POST"])
@jwt_required()
@admin_required
def create_user():
    data = request.json
    new_usr = User(data["username"], data["chips"], data["password"]) 
    try:
        db.session.add(new_usr)
        db.session.commit()    
    except IntegrityError as e:
        abort(500) # username taken
    return jsonify(new_usr.to_dict()), 201