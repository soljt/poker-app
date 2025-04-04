from app.util import util
from app.db import db
from app.models.user import User

@util.route("/make-sol", methods=["GET"])
def add_user():
    new_usr = User("kenna", 1000, "ilovemybf") # soljt password: pass
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
    return f"<h1>DELETED USERS:</h1>\n{"".join(f"<p>{user.username}</p>\n" for user in users)}"