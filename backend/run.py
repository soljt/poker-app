import os
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV") != "production"
    socketio.run(app, debug=debug)