import { useAuth } from "../context/useAuth";

const HostGameManager = () => {
  const { socket, user } = useAuth();
  function handleStartGame() {
    socket?.emit("start_game");
  }

  function handleCreateGame() {
    const username = user?.username;
    socket?.emit("create_game", { username });
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
