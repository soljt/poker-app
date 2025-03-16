import { useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://127.0.0.1:5000"); // Flask WebSocket Server

interface JoinGameProps {
    setPlayer: (player: string) => void;
}

function JoinGame({ setPlayer }: JoinGameProps) {
  const [username, setUsername] = useState("");
  const [chips, setChips] = useState("");

  const joinGame = () => {
    socket.emit("join", { username, chips: parseInt(chips) });

    socket.on("joined", (data) => {
      alert(data.message);
      setPlayer(username); // Save username in state
    });

    socket.on("error", (data) => {
      alert(data.message);
    });
  };

  return (
    <div>
      <h2>Enter Your Name and Chips</h2>
      <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="number" placeholder="Chips" value={chips} onChange={(e) => setChips(e.target.value)} />
      <button onClick={joinGame}>Join Game</button>
    </div>
  );
}

export default JoinGame;