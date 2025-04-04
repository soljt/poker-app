from sqlite3 import IntegrityError
from app.auth import auth
from app.db import db
from app.models.user import User
from flask import (
    request,
    jsonify,
)
from flask_jwt_extended import (
    create_access_token, 
    current_user, 
    jwt_required, 
    set_access_cookies, 
    unset_jwt_cookies
)

@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    user = db.session.execute(db.select(User).filter_by(username=data["username"])).scalar_one_or_none()
    if not user:
        return jsonify({"error": "Username not found"}), 404
    if not user.check_password(data["password"]):
        return jsonify({"error": "Incorrect password"}), 401
    
    # TODO TOKEN
    access_token = create_access_token(identity=user) # can pass user object due to jwt.user_identity_loader
    response = jsonify({"message": "Login successful from backend"})
    try:
        set_access_cookies(response, access_token)
    except Exception as e:
        print(f"error: {e}")
        return jsonify({"error": "server-side"}), 500
    return response

@auth.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful from backend"})
    unset_jwt_cookies(response)
    return response

@auth.route("/register", methods=["POST"])
def register():
    data = request.json
    new_usr = User(data["username"], data["chips"], data["password"]) 
    try:
        db.session.add(new_usr)
        db.session.commit()    
    except IntegrityError as e:
        return jsonify({"error": "Username taken"}), 500

    # TODO TOKEN - OR MAYBE NOT - make the user enter their new details to login
    # access_token = create_access_token(identity=data["username"])
    response = jsonify({"message": "Registration successful from backend"})
    # try:
    #     set_access_cookies(response, access_token)
    # except Exception as e:
    #     print(f"error: {e}")
    #     return jsonify({"error": "server-side"}), 500
    return response

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@auth.route("/who_am_i", methods=["POST"])
@jwt_required()
def who_am_i():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify({"user": current_user.to_dict()})