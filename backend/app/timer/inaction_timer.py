import threading
import time

class InactionTimer:
    def __init__(
        self,
        socketio,
        app,
        game_id: str,
        username: str,
        delay: int = 30,
        get_game_callback=None,  # () => Game
        kick_callback=None       # (username, game_id) => None
    ):
        self.socketio = socketio
        self.app = app
        self.game_id = game_id
        self.username = username
        self.delay = delay

        self.get_game_callback = get_game_callback
        self.kick_callback = kick_callback

        self.kick_timer = None
        self.countdown_thread = None
        self.cancel_event = threading.Event()

    def start(self):
        self.cancel_event.clear()
        self.countdown_thread = threading.Thread(target=self._emit_countdown)
        self.countdown_thread.start()

        self.kick_timer = threading.Timer(self.delay, self._kick_player)
        self.kick_timer.start()

    def cancel(self):
        self.cancel_event.set()
        if self.kick_timer:
            self.kick_timer.cancel()

    def cleanup(self):
        self.kick_timer = None
        self.countdown_thread = None
        self.socketio = None
        self.app = None
        self.get_game_callback = None
        self.kick_callback = None

    def _emit_countdown(self):
        seconds_left = self.delay
        while seconds_left >= 0 and not self.cancel_event.is_set():
            self.socketio.emit("kick_countdown", {"seconds": seconds_left}, to=self.username)
            time.sleep(1)
            seconds_left -= 1

    def _kick_player(self):
        if self.cancel_event.is_set():
            return
        with self.app.app_context():
            game = self.get_game_callback(self.game_id) if self.get_game_callback else None
            if not game or str(game.current_player) != self.username:
                return
            self.socketio.emit("error", {"message": f"User {self.username} kicked for inaction!"}, to=self.game_id)
            self.socketio.emit("player_kicked", to=self.username)
            if self.kick_callback:
                self.kick_callback(self.game_id, self.username)

    # def __del__(self):
    #     print(f"Timer for {self.username} in {self.game_id} deleted!")
