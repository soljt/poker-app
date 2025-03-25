import { useState, useEffect } from "react";
import { socket } from "../socket.tsx";
import { ConnectionState } from "../components/ConnectionState.tsx";
// import { ConnectionManager } from "./components/ConnectionManager.tsx";
import { CheckIn } from "../components/CheckIn.tsx";

export default function Landing() {
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

  return (
    <div className="App">
      <ConnectionState isConnected={isConnected} />
      <CheckIn />
    </div>
  );
}
