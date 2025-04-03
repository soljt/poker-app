import { useAuth } from "../context/useAuth";

const HostGameManager = () => {
  const { socket, user } = useAuth();
  function handleStartGame() {
    socket?.emit("start_game", { game_id: localStorage.getItem("game_id") });
  }

  function handleCreateGame() {
    const username = user?.username;
    socket?.emit("create_game", { username }, (game_id: string) => {
      localStorage.setItem("game_id", game_id);
    });
  }

  return (
    <div className="vstack gap-3">
      <button className="btn btn-lg btn-info" onClick={handleCreateGame}>
        Create Game
      </button>
      <button className="btn btn-lg btn-success" onClick={handleStartGame}>
        Start Game
      </button>
    </div>
  );
};

export default HostGameManager;
