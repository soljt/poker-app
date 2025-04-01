import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ConnectionState } from "../components/ConnectionState.tsx";
import { ConnectionManager } from "../components/ConnectionManager.tsx";
import { useAuth } from "../context/useAuth.tsx";

export default function Lobby() {
  const { socket } = useAuth();
  const navigate = useNavigate();
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
    }
    socket?.on("connect", onConnect);
    socket?.on("disconnect", onDisconnect);

    return () => {
      socket?.off("connect", onConnect);
      socket?.off("disconnect", onDisconnect);
    };
  });

  useEffect(() => {
    function startGame() {
      navigate("/game");
    }
    socket?.on("game_started", startGame);

    return () => {
      socket?.off("game_started", startGame); // Cleanup listener on unmount
    };
  }, [navigate, socket]);

  return (
    <div className="container">
      <p>Waiting for game to start...</p>
      <ConnectionState isConnected={isConnected} />
      <ConnectionManager />
    </div>
  );
}
