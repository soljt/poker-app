import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth.tsx";
import HostGameManager from "../components/HostGameManager.tsx";
import { toast } from "react-toastify";

export default function Lobby() {
  const { socket, user } = useAuth();
  const navigate = useNavigate();
  const [games, setGames] = useState<{ game_id: string; host: string }[]>([]);

  useEffect(() => {
    socket?.emit(
      "get_games",
      (gameList: { game_id: string; host: string }[]) => {
        setGames(gameList);
      }
    ); // Request list on load

    const startGame = (data: { message: string }) => {
      toast.success(data.message);
      navigate("/game");
    };

    socket?.on("game_created", (game) => {
      setGames((prev) => [...prev, game]); // Update game list when a new game is created
    });

    socket?.on("game_deleted", (game) => {
      if (localStorage.getItem("game_id") === game.game_id) {
        localStorage.removeItem("game_id");
      }
      setGames((prev) => prev.filter((entry) => entry.game_id != game.game_id));
    });

    socket?.on("player_joined", (data) => {
      toast.info(`${data.username} joined ${data.game_id}`);
    });

    // socket?.on("")

    socket?.on("game_started", startGame);

    return () => {
      socket?.off("game_created");
      socket?.off("player_joined");
      socket?.off("game_deleted");
      socket?.off("game_started", startGame); // Cleanup listener on unmount
    };
  }, [navigate, socket]);

  const joinGame = (game_id: string) => {
    const username = user?.username;
    socket?.emit(
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
    socket?.emit("delete_game", { game_id, username });
  };

  const leaveGame = (game_id: string, username: string) => {
    socket?.emit("leave_game", { game_id, username }, () => {
      localStorage.removeItem("game_id");
    });
  };

  return (
    <>
      {user?.username === "soljt" && (
        <div className="container p-3">
          <HostGameManager />
        </div>
      )}
      <div className="container">
        <ul className="list-group">
          {games.map((game) => (
            <li className="list-group-item" key={game.game_id}>
              {game.host}'s game{" "}
              <button
                className="btn btn-primary"
                onClick={() => joinGame(game.game_id)}
              >
                Join
              </button>
              {game.host === user?.username ? (
                <button
                  className="btn btn-danger"
                  onClick={() => deleteGame(game.game_id, user.username)}
                >
                  Delete
                </button>
              ) : (
                <button
                  className="btn btn-danger"
                  onClick={() =>
                    user?.username && leaveGame(game.game_id, user.username)
                  }
                >
                  Leave Game
                </button>
              )}
            </li>
          ))}
        </ul>
      </div>
    </>
  );
}
