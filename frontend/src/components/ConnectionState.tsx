import { useEffect, useState } from "react";
import { Socket } from "socket.io-client";

export function ConnectionState({ socket }: { socket: Socket | null }) {
  const [isConnected, setIsConnected] = useState(socket?.active || false);
  useEffect(() => {
    setIsConnected(socket?.active || false);
    console.log("called connection state useEffect");
    socket?.on("test", () => console.log("test"));
    return () => {
      socket?.off("test");
    };
  }, [socket]);
  return (
    <i
      className="bi bi-circle-fill"
      style={{ color: isConnected ? "green" : "red", fontSize: "2rem" }}
    ></i>
  );
}
