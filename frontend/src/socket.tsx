import { io, Socket } from "socket.io-client";
import { handleError } from "./helpers/ErrorHandler";

const URL = "http://localhost:5000";

export const createSocket = (): Socket | null => {
  try {
    const socket = io(URL, {
      withCredentials: true,
    });
    return socket;
  } catch (error: unknown) {
    handleError(error);
    return null;
  }
};
