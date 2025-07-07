from flask import request
from flask_socketio import emit, join_room, leave_room, SocketIO
from app.extensions import socketio
from app.globals import connected_users, games
from flask_jwt_extended import decode_token
from app.models.user import User
from app.db import db
from app.sockets.lobby_events import handle_delete_game


@socketio.on("connect")
def connect_handler(auth):
    print(f"New connection attempt with SID: {request.sid}")
    if not request.cookies:
        print("no cookies!")
        return False
    try: 
        decoded = decode_token(request.cookies["access_token_cookie"], request.cookies["csrf_access_token"])   
        user_id = decoded["sub"]
        username = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none().username   
        print(f"connected successfully with {request.sid}")
        print(f"from global_events.py: {request.sid} joined room: {username}")
        join_room(username)
        # check to see if user is reconnecting under different sid
        for key, dic in connected_users.items():
            if dic.get("username") == username:
                # get the user's joined game and rejoin it
                game_id = dic.get("game_id")
                if game_id:
                    join_room(game_id)
                    emit("message", f"User {username} reconnected!", to=game_id)

                # delete old entry
                del connected_users[key]
                connected_users[request.sid] = dic              
                return
        
        # if this is the first connection, add user to connected_users
        connected_users[request.sid] = {"username": username, "game_id": None}
    except:
        print("failed")
        return False


@socketio.on("disconnect")
def disconnect_handler(reason):
    print(f"closing connection with SID: {request.sid} due to {reason}")
    try:
        username = connected_users.get(request.sid).get("username")
        room = connected_users.get(request.sid).get("game_id")

        # TODO: handle disconnection from active game...remove the player? what
        # could use reason.SERVER_DISCONNECT to detect when server kicks due to inactivity

        # # if the user logged off intentionally
        # if reason == SocketIO.reason.CLIENT_DISCONNECT:
        #     if room:
        #         games[room]["players"].remove(username)
        #         emit("error", {"message": f"User {username} logged off"}, to=room)
        #         leave_room(room)
        #         if username == games[room]["host"]:
        #             handle_delete_game({"game_id": room})
        #     del connected_users[request.sid]
        
        # # if they logged off, hopefully with the intent to reconnect...
        # # TODO: should implement some sort of timer to eventually remove them from connected_users and games
        # else:
        
        emit("error", {"message": f"User {username} disconnected :("}, to=room)
    except AttributeError as e:
        print(e)