import { useSocket } from "../context/useSocket";

export function ConnectionManager() {
  const socket = useSocket();
  function connect() {
    socket?.connect();
  }

  function disconnect() {
    socket?.disconnect();
  }

  return (
    <div className="align-items-center gap-3">
      <button className="btn btn-primary btn-lg" onClick={connect}>
        Connect
      </button>
      <button className="btn btn-dark btn-lg" onClick={disconnect}>
        Disconnect
      </button>
    </div>
  );
}
