import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { socket } from "../socket.tsx";

export default function Lobby() {
  const navigate = useNavigate();

  useEffect(() => {
    function startGame() {
      navigate("/game");
    }
    socket.on("game_started", startGame);

    return () => {
      socket.off("game_started", startGame); // Cleanup listener on unmount
    };
  }, [navigate]);

  return <p>Waiting for game to start...</p>;
}
