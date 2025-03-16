import { useState, useEffect } from "react";
import { io } from "socket.io-client";

const socket = io("http://127.0.0.1:5000");

interface PokerGameProps {
    player: string |null
}

function PokerGame({ player }: PokerGameProps) {
  const [hand, setHand] = useState<string[]>([]);
  
  useEffect(() => {
    // Listen for the player's hand
    socket.on("your_hand", (data) => {
      setHand(data.cards);
    });
  }, []);

  const startGame = () => {
    socket.emit("start_game");
  };

  return (
    <div>
      <h2>Welcome, {player}</h2>
      {hand.length > 0 ? (
        <div>
          <h3>Your Hand:</h3>
          <p>{hand.join(", ")}</p>
        </div>
      ) : (
        <p>Waiting for game to start...</p>
      )}

      {player === "host" && <button onClick={startGame}>Start Game</button>}
    </div>
  );
}

export default PokerGame;