from app import create_app
from app.extensions import socketio  # or from app import socketio if it's defined there

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True)