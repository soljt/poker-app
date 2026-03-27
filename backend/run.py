import os
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == "__main__":
    debug = allow_unsafe_werkzeug = os.getenv("FLASK_ENV") != "production"
    socketio.run(app, debug=debug, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=allow_unsafe_werkzeug)