import { useState } from "react";
import JoinGame from "./JoinGame";
import PokerGame from "./PokerGame";

function App() {
  const [player, setPlayer] = useState("");

  return (
    <div>
      {player ? <PokerGame player={player} /> : <JoinGame setPlayer={setPlayer} />}
    </div>
  );
}

export default App;