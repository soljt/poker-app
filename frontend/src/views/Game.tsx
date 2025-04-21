import { useEffect, useState } from "react";
import { game_api } from "../services/api";
import { handleError } from "../helpers/ErrorHandler";
import { toast } from "react-toastify";
import PokerGamePage from "../components/PokerGamePage";
import PlayerActionPanel from "../components/PlayerActionPanel";
import RoundOverOverlay from "../components/RoundOverOverlay";
import { GameData, PlayerTurnData, ActionItem, PotAwardItem } from "../types";
import { useAuth } from "../context/useAuth";

const Game = () => {
  const [gameData, setGameData] = useState<GameData | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [playerToAct, setPlayerToAct] = useState("");
  const [actionList, setActionList] = useState<Array<ActionItem> | null>(null);
  const [showRoundOver, setShowRoundOver] = useState(false);
  const [potAwards, setPotAwards] = useState<PotAwardItem[]>([]);
  const [host, setHost] = useState("");
  const { socket, user } = useAuth();

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
            setPlayerToAct(response.data.player_to_act);
            setActionList(response.data.available_actions);
            console.log("available actions:", response.data.available_actions);
          }
        });
    } catch (error) {
      handleError(error);
    }
  }, []);

  useEffect(() => {
    try {
      game_api
        .get("/host", { params: { game_id: localStorage.getItem("game_id") } })
        .then((response) => {
          if (response.data.error) {
            toast.warn(response.data.error);
            setErrorMessage(response.data.error);
          } else {
            setHost(response.data.host);
          }
        });
    } catch (error) {
      handleError(error);
    }
  }, []);

  const handlePlayerTurn = (data: PlayerTurnData) => {
    console.log("received:", data);
    setPlayerToAct(data.player_to_act);
    setActionList(data.available_actions);
  };

  const updateGameState = (data: GameData) => {
    console.log("updating game state:", data);
    setGameData(data);
  };

  const handleStartNextRound = () => {
    socket?.emit("start_next_round");
    setShowRoundOver(false);
    setPotAwards([]);
  };

  useEffect(() => {
    console.log("Socket status:", socket?.connected);
    socket?.on("player_turn", handlePlayerTurn);
    socket?.on("update_game_state", updateGameState);
    socket?.on("round_over", (data: PotAwardItem[]) => {
      setPotAwards(data);
      setShowRoundOver(true);
    });
    return () => {
      socket?.off("player_turn", handlePlayerTurn);
      socket?.off("update_game_state");
      socket?.off("round_over");
    };
  }, [socket]);

  return (
    <>
      {gameData && <PokerGamePage gameData={gameData} />}
      <RoundOverOverlay
        show={showRoundOver}
        potAwards={potAwards}
        onClose={() => setShowRoundOver(false)}
        isHost={host === user?.username} // determine based on logged-in user
        onStartNextRound={handleStartNextRound}
      />

      {user?.username === playerToAct && (
        <PlayerActionPanel
          availableActions={
            actionList || [{ action: "Nothing", min: 0, allin: false }]
          }
          onActionSelect={(action: string, amount?: number) => {
            socket?.emit("player_action", {
              player: user.username,
              action,
              amount: amount ?? null,
            });
            console.log(
              "sent to backend...player:",
              user.username,
              "action:",
              action,
              "amount:",
              amount ?? null
            );
          }}
        />
      )}
      <div className="container">
        <h4 className="text-center" style={{ color: "red" }}>
          {errorMessage}
        </h4>
      </div>
    </>
  );
};

export default Game;
