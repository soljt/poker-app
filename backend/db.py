from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()  # Create a database instance

def init_db(app):
    """Initialize the database with the Flask app."""
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI  # SQLite file
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    print("DB INITIALIZED")
    db.init_app(app)  # Bind database to the Flask app

    with app.app_context():  # Create tables if they don't exist
        print("TABLES CREATED")
        db.create_all()

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    chips = db.Column(db.Integer, default=1000)

    def __init__(self, username, chips, password):
        self.username = username
        self.chips = chips
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "chips": self.chips}