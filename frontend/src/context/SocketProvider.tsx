// SocketProvider.tsx
import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { io, Socket } from "socket.io-client";
import {
  handleSocketError,
  handleSocketMessage,
} from "../helpers/SocketAlertHandler";
import { ConnectionState } from "../components/ConnectionState";

const SocketContext = createContext<Socket | null>(null);

export const SocketProvider = ({ children }: { children: React.ReactNode }) => {
  const ws = useRef<Socket | null>(null);

  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const socket = io("http://localhost:5000", { withCredentials: true });
    socket.on("connect", () => {
      console.log("Socket connected: ", socket.id);
      setIsReady(true);
    });
    socket.on("disconnect", () => {
      console.log("Socket disconnected: ", socket.id);
      setIsReady(false);
    });
    // Handle global socket errors
    socket?.on("error", handleSocketError);
    socket?.on("message", handleSocketMessage);

    ws.current = socket;
    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <SocketContext.Provider value={ws.current}>
      {isReady ? (
        <>
          <div>
            <ConnectionState socket={ws.current} />
            <p>{ws.current?.id}</p>
          </div>{" "}
          {children}
        </>
      ) : (
        <div>Loading socket connection...</div>
      )}
    </SocketContext.Provider>
  );
};

export function useSocket() {
  const socket = useContext(SocketContext);
  if (!socket) {
    throw new Error("useSocket must be used within a SocketProvider");
  }
  return socket;
}
