games = {} # games[game_id] = {"players" : [], "host": str, "game": PokerRound} - "game" is not set until game is started by host
connected_users = {} # active_users[socket_sid] = {"username": str, "game_id": str} - user doesn't become "active" unless they get a game_id, otherwise null
