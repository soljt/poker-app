import { useEffect, useState } from "react";
import { game_api } from "../services/api";
import { handleError } from "../helpers/ErrorHandler";
import { toast } from "react-toastify";
import PokerGamePage from "../components/PokerGamePage";
import { GameData } from "../types";

const Game = () => {
  const [gameData, setGameData] = useState<GameData | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  // should also handle REDIRECTING user if they have no "game_id" localStorage or
  // if they are not in the game they try to join

  useEffect(() => {
    try {
      game_api
        .get("/state", { params: { game_id: localStorage.getItem("game_id") } })
        .then((response) => {
          if (response.data.error) {
            toast.warn(response.data.error);
            setErrorMessage(response.data.error);
          } else {
            setGameData(response.data);
          }
        });
    } catch (error) {
      handleError(error);
    }
  }, []);

  return (
    <>
      {gameData && <PokerGamePage gameData={gameData} />}
      <div className="container">
        <h4 className="text-center" style={{ color: "red" }}>
          {errorMessage}
        </h4>
      </div>
    </>
  );
};

export default Game;
