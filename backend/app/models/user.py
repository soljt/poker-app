from werkzeug.security import generate_password_hash, check_password_hash
from app.db import db
import enum

class RoleEnum(enum.Enum):
    player = "player"
    host = "host"
    admin = "admin"

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.Text)
    chips = db.Column(db.Integer, default=1000)
    role = db.Column(db.Enum(RoleEnum), default=RoleEnum.host)

    def __init__(self, username, chips, password, role=RoleEnum.player):
        self.username = username
        self.chips = chips
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "chips": self.chips, "role": self.role.value}