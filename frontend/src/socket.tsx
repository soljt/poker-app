import { io, Socket } from "socket.io-client";
import { handleError } from "./helpers/ErrorHandler";
import {
  handleSocketError,
  handleSocketMessage,
} from "./helpers/SocketAlertHandler";

const URL = "http://localhost:5000";

export const createSocket = (): Socket | null => {
  try {
    const socket = io(URL, {
      withCredentials: true,
    });

    // Handle global socket errors
    socket.on("error", handleSocketError);

    socket.on("message", handleSocketMessage);

    return socket;
  } catch (error: unknown) {
    handleError(error);
    return null;
  }
};
