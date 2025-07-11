import os
from app.util import util
from app.db import db
from app.models.user import User

if os.environ.get("FLASK_ENV") != "production":
    @util.route("/make_users", methods=["GET"])
    def add_user():
        new_usr = User("soljt", 1000, "pass", "admin")
        db.session.add(new_usr)
        new_usr = User("kenna", 500, "ilovemybf", "player") # soljt password: pass
        db.session.add(new_usr)
        new_usr = User("hotbrian", 1000, "password12345", "player")
        db.session.add(new_usr)
        db.session.commit()
        return f"<h1>SUCCESS</h1>"

    @util.route("/delete-users", methods=["GET"])
    def delete_users():
        users = db.session.execute(db.select(User).filter(User.username.not_in(["soljt", "kenna"]))).scalars().fetchall()
        for user in users:
            db.session.delete(user)
        
        db.session.commit()
        # db.session.commit()
        deleted_users = [f"<p>{user.username}</p>\n" for user in users]
        return f"<h1>DELETED USERS:</h1>\n{''.join(deleted_users)}"