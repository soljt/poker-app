import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { socket } from "../socket.tsx";
import { ConnectionState } from "../components/ConnectionState.tsx";

export default function Lobby() {
  const [isConnected, setIsConnected] = useState(socket.connected);

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
    }

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);

    return () => {
      socket.off("connect", onConnect);
      socket.off("disconnect", onDisconnect);
    };
  }, []);
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

  return (
    <>
      <p>Waiting for game to start...</p>
      <ConnectionState isConnected={isConnected} />
    </>
  );
}
