from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Create a database instance

def init_db(app):
    """Initialize the database with the Flask app."""
    print("DB INITIALIZED")
    db.init_app(app)  # Bind database to the Flask app

    with app.app_context():  # Create tables if they don't exist
        print("TABLES CREATED")
        db.create_all()