from sqlite3 import IntegrityError
from app.auth import auth
from app.auth.demo import DEMO_CHIPS, AllSeatsBusyError, demo_leases, is_demo_username, verify_turnstile
from app.db import db
from app.extensions import limiter
from app.models.user import User
from app.sockets.helpers import evict_user, is_in_started_game
from flask import (
    request,
    jsonify,
)
from flask_jwt_extended import (
    create_access_token, 
    current_user, 
    get_jwt,
    jwt_required, 
    set_access_cookies, 
    unset_jwt_cookies,
    verify_jwt_in_request
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

@auth.route("/demo", methods=["POST"])
@limiter.limit("10 per hour")
def demo_login():
    data = request.json or {}
    if not verify_turnstile(data.get("turnstile_token"), request.remote_addr):
        return jsonify({"error": "Couldn't verify you're human - try again"}), 403
    try:
        lease = demo_leases.claim(is_busy=is_in_started_game)
    except AllSeatsBusyError as e:
        minutes = max(e.retry_after // 60, 1)
        return jsonify({"error": f"All demo seats are in use - try again in ~{minutes} min, or register (takes 10 seconds)"}), 503

    # whoever had this seat before is gone - clear them out and reset the chips
    evict_user(lease.username)
    user = db.session.execute(db.select(User).filter_by(username=lease.username)).scalar_one()
    user.chips = DEMO_CHIPS
    db.session.commit()

    access_token = create_access_token(identity=user, additional_claims={"lease_id": lease.lease_id})
    response = jsonify({"message": f"Logged in as {user.username}"})
    set_access_cookies(response, access_token)
    return response

@auth.route("/logout", methods=["POST"])
def logout():
    try:
        verify_jwt_in_request(optional=True)
        lease_id = get_jwt().get("lease_id")
        if lease_id:
            demo_leases.release(current_user.username, lease_id)
    except Exception:
        pass
    response = jsonify({"message": "Logout successful from backend"})
    unset_jwt_cookies(response)
    return response

@auth.route("/register", methods=["POST"])
def register():
    data = request.json
    if is_demo_username(data["username"]):
        return jsonify({"error": "Username taken"}), 500
    new_usr = User(username=data["username"], chips=5000, password=data["password"]) 
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