import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth.tsx";
import HostGameManager from "../components/HostGameManager.tsx";
import { toast } from "react-toastify";
import { GameParams, LobbyEntry } from "../types.ts";
import LobbyList from "../components/LobbyList.tsx";
import { Roles } from "../types.ts";
import { useSocket } from "../context/useSocket.tsx";

export default function Lobby() {
  const { user, refreshUser } = useAuth();
  const socket = useSocket();
  const navigate = useNavigate();
  const [games, setGames] = useState<LobbyEntry[]>([]);

  if (!user) {
    throw new Error("Must be logged in to have access to user variable");
  }

  const joinGame = (game_id: string) => {
    const username = user?.username;
    socket.emit(
      "join_game",
      { game_id, username },
      (game_id: string | null) => {
        if (game_id) {
          localStorage.setItem("game_id", game_id);
        }
      }
    );
  };

  const deleteGame = (game_id: string, username: string) => {
    socket.emit("delete_game", { game_id, username });
  };

  const leaveGame = (game_id: string, username: string) => {
    socket.emit("leave_game", { game_id, username }, () => {
      localStorage.removeItem("game_id");
    });
  };

  function handleCreateGame(gameParams: GameParams) {
    socket.emit("create_game", gameParams, (game_id: string) => {
      localStorage.setItem("game_id", game_id);
    });
  }

  function handleStartGame() {
    socket.emit("start_game", { game_id: localStorage.getItem("game_id") });
  }

  function reconnectToGame(game_id: string) {
    socket.emit("reconnect_to_game", { game_id }, (status: boolean) => {
      if (status) {
        localStorage.setItem("game_id", game_id);
        navigate("/game");
      }
    });
  }

  // Request list on load
  useEffect(() => {
    socket.emit("get_games", (gameList: LobbyEntry[]) => {
      setGames(gameList);
      console.log("received on refresh:", gameList);
    });
  }, [socket]);

  // create all event listeners...would it be better to just have send the new games list from the backend
  // every time it changes with a "games_updated" event or something, rather than iterating over all games
  // each time a player leaves/joins a game?
  useEffect(() => {
    console.log(socket.id);
    const startGame = (data: { message: string }) => {
      toast.success(data.message);
      navigate("/game");
    };

    socket.on("game_created", (game) => {
      setGames((prev) => [...prev, game]); // Update game list when a new game is created
      console.log("new game:", game);
    });

    socket.on("game_deleted", (game) => {
      if (localStorage.getItem("game_id") === game.game_id) {
        localStorage.removeItem("game_id");
      }
      refreshUser();
      setGames((prev) => prev.filter((entry) => entry.game_id != game.game_id));
    });

    socket.on("player_joined", (data) => {
      setGames((prevGames) =>
        prevGames.map((game) => {
          if (game.game_id === data.game_id) {
            return {
              ...game,
              players: [...game.players, data.username],
            };
          }
          return game;
        })
      );
    });

    socket.on("player_queued", (data) => {
      setGames((prevGames) =>
        prevGames.map((game) => {
          if (game.game_id === data.game_id) {
            return {
              ...game,
              joiner_queue: [...game.joiner_queue, data.username],
            };
          }
          return game;
        })
      );
    });

    socket.on("player_left", (data) => {
      setGames((prevGames) =>
        prevGames.map((game) => {
          if (game.game_id === data.game_id) {
            return {
              ...game,
              players: game.players.filter((name) => name != data.username),
            };
          }
          return game;
        })
      );
    });

    socket.on("player_dequeued", (data) => {
      setGames((prevGames) =>
        prevGames.map((game) => {
          if (game.game_id === data.game_id) {
            return {
              ...game,
              joiner_queue: game.joiner_queue.filter(
                (name) => name != data.username
              ),
            };
          }
          return game;
        })
      );
    });

    socket.on("player_removed", (game_id) => {
      localStorage.setItem("game_id", "");
      socket.emit("leave_room", {
        game_id,
      });
    });

    socket.on("game_started", startGame);

    socket.on("chips_updated", () => {
      refreshUser();
    });

    return () => {
      console.log("cleanup");
      socket.off("game_created");
      socket.off("player_joined");
      socket.off("game_deleted");
      socket.off("game_started", startGame); // Cleanup listener on unmount
      socket.off("player_left");
      socket.off("player_queued");
      socket.off("player_dequeued");
      socket.off("chips_updated");
    };
  }, [navigate, socket, refreshUser]);

  return (
    <>
      <div className="container my-4">
        <h2 className="text-center mb-4">Lobby</h2>
      </div>
      {user && (user.role === Roles.host || user.role === Roles.admin) && (
        <div className="container p-3">
          <HostGameManager handleCreateGame={handleCreateGame} />
        </div>
      )}
      <LobbyList
        games={games}
        user={user}
        joinGame={joinGame}
        deleteGame={deleteGame}
        leaveGame={leaveGame}
        handleStartGame={handleStartGame}
        reconnectToGame={reconnectToGame}
      />
    </>
  );
}
