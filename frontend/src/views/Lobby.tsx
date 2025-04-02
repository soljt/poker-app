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
    function startGame() {
      navigate("/game");
    }

    socket?.emit("get_games"); // Request list on load

    socket?.on("available_games", (gameList) => {
      console.log(gameList);
      setGames(gameList);
    });

    socket?.on("game_created", (game) => {
      setGames((prev) => [...prev, game]); // Update game list when a new game is created
    });

    socket?.on("game_deleted", (game) => {
      setGames((prev) => prev.filter((entry) => entry.game_id != game.game_id));
    });

    socket?.on("player_joined", (data) => {
      toast.info(`${data.username} joined ${data.game_id}`);
    });

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
    socket?.emit("join_game", { game_id, username });
  };

  const deleteGame = (game_id: string, username: string) => {
    socket?.emit("delete_game", { game_id, username });
  };

  return (
    <div className="container p-3">
      {user?.username === "soljt" ? <HostGameManager /> : <></>}
      <ul>
        {games.map((game) => (
          <li key={game.game_id}>
            {game.host}'s game{" "}
            <button
              className="btn btn-primary"
              onClick={() => joinGame(game.game_id)}
            >
              Join
            </button>
            {game.host === user?.username && (
              <button
                className="btn btn-danger"
                onClick={() => deleteGame(game.game_id, user.username)}
              >
                Delete
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
