import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth.tsx";
import HostGameManager from "../components/HostGameManager.tsx";
import { toast } from "react-toastify";
import { LobbyEntry } from "../types.ts";
import LobbyList from "../components/LobbyList.tsx";
import { Roles } from "../types.ts";
import { useSocket } from "../context/useSocket.tsx";

export default function Lobby() {
  const { user } = useAuth();
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

  function handleCreateGame() {
    const username = user?.username;
    socket.emit("create_game", { username }, (game_id: string) => {
      localStorage.setItem("game_id", game_id);
    });
  }

  function handleStartGame() {
    socket.emit("start_game", { game_id: localStorage.getItem("game_id") });
  }

  function reconnectToGame() {
    navigate("/game");
  }

  useEffect(() => {
    socket.emit("get_games", (gameList: LobbyEntry[]) => {
      setGames(gameList);
      console.log("received on refresh:", gameList);
    }); // Request list on load
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
      setGames((prev) => prev.filter((entry) => entry.game_id != game.game_id));
    });

    socket.on("player_joined", (data) => {
      toast.info(`${data.username} joined ${data.game_id}`);
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
      toast.info(`${data.username} queued for ${data.game_id}`);
      setGames((prevGames) =>
        prevGames.map((game) => {
          if (game.game_id === data.game_id) {
            return {
              ...game,
              queue: [...game.queue, data.username],
            };
          }
          return game;
        })
      );
    });

    socket.on("player_left", (data) => {
      toast.info(`${data.username} left ${data.game_id}`);
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
      toast.info(`${data.username} dequeued from ${data.game_id}`);
      setGames((prevGames) =>
        prevGames.map((game) => {
          if (game.game_id === data.game_id) {
            return {
              ...game,
              queue: game.queue.filter((name) => name != data.username),
            };
          }
          return game;
        })
      );
    });

    socket.on("game_started", startGame);

    return () => {
      console.log("cleanup");
      socket.off("game_created");
      socket.off("player_joined");
      socket.off("game_deleted");
      socket.off("game_started", startGame); // Cleanup listener on unmount
      socket.off("player_left");
      socket.off("player_queued");
      socket.off("player_dequeued");
    };
  }, [navigate, socket]);

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
