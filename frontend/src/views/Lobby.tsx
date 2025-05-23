import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth.tsx";
import HostGameManager from "../components/HostGameManager.tsx";
import { toast } from "react-toastify";
import { LobbyEntry } from "../types.ts";
import LobbyList from "../components/LobbyList.tsx";
import { Roles } from "../types.ts";
import { useSocket } from "../context/SocketProvider.tsx";

export default function Lobby() {
  const { user } = useAuth();
  const socket = useSocket();
  const navigate = useNavigate();
  const [games, setGames] = useState<LobbyEntry[]>([]);

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

  useEffect(() => {
    socket.emit("get_games", (gameList: LobbyEntry[]) => {
      setGames(gameList);
    }); // Request list on load
  }, [socket]);

  useEffect(() => {
    console.log(socket.id);
    const startGame = (data: { message: string }) => {
      toast.success(data.message);
      navigate("/game");
    };

    socket.on("game_created", (game) => {
      setGames((prev) => [...prev, game]); // Update game list when a new game is created
      console.log("new game:", game);
      // console.log("games list:", games);
    });

    socket.on("game_deleted", (game) => {
      if (localStorage.getItem("game_id") === game.game_id) {
        localStorage.removeItem("game_id");
      }
      setGames((prev) => prev.filter((entry) => entry.game_id != game.game_id));
    });

    socket.on("player_joined", (data) => {
      toast.info(`${data.username} joined ${data.game_id}`);
    });

    // socket?.on("")

    socket.on("game_started", startGame);

    return () => {
      console.log("cleanup");
      socket.off("game_created");
      socket.off("player_joined");
      socket.off("game_deleted");
      socket.off("game_started", startGame); // Cleanup listener on unmount
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
      />
    </>
  );
}
