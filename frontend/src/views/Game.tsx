import { useEffect, useState } from "react";
import { useAuth } from "../context/useAuth";

const Game = () => {
  const [hand, setHand] = useState<string[]>([]);
  const { socket } = useAuth();
  useEffect(() => {
    console.log("Hand updated:", hand);
  }, [hand]); // Runs whenever hand changes

  useEffect(() => {
    // Listen for the player's hand
    socket?.emit("get_hand", (cards: string[]) => {
      setHand(cards);
    });
  }, [socket]);

  return (
    <div className="container">
      <h4>My Hand:</h4>
      <ul>
        {hand.map((card, i) => (
          <li key={"card " + i}>{card}</li>
        ))}
      </ul>
    </div>
  );
};

export default Game;
