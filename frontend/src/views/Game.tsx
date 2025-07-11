import { useEffect, useState } from "react";
import { game_api } from "../services/api";
import { handleError } from "../helpers/ErrorHandler";
import { toast } from "react-toastify";
import PokerGamePage from "../components/PokerGamePage";
import PlayerActionPanel from "../components/PlayerActionPanel";
import RoundOverOverlay from "../components/NewRoundOverOverlay";
import { GameData, PlayerTurnData, ActionItem, PotAwardItem } from "../types";
import { useAuth } from "../context/useAuth";
import { useSocket } from "../context/useSocket";
import { Button, Col, Container, Row } from "react-bootstrap";
import ConfirmActionModal from "../components/ConfirmActionModel";
import { useNavigate } from "react-router-dom";
import HandRankModal from "../components/HandRankModal";

const Game = () => {
  const [gameData, setGameData] = useState<GameData | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [playerToAct, setPlayerToAct] = useState("");
  const [actionList, setActionList] = useState<Array<ActionItem> | null>(null);
  const [showRoundOver, setShowRoundOver] = useState(false);
  const [countDownTimer, setCountDownTimer] = useState(999);
  const [kickTimer, setKickTimer] = useState(999);
  const [potAwards, setPotAwards] = useState<PotAwardItem[]>([]);
  const [host, setHost] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);
  const [actionType, setActionType] = useState<"leave" | "end" | null>(null);
  const [revealedHands, setRevealedHands] = useState<Record<string, string[]>>(
    {}
  );
  const { user } = useAuth();
  const socket = useSocket();
  const navigate = useNavigate();

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
          } else {
            setHost(response.data.host);
            console.log("host set as:", response.data.host);
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
    setShowRoundOver(false);
  };

  useEffect(() => {
    console.log("Socket status:", socket?.connected);
    socket.on("player_turn", handlePlayerTurn);
    socket.on("update_game_state", updateGameState);
    socket.on("round_over", (data: PotAwardItem[]) => {
      setPotAwards(data);
      setShowRoundOver(true);
    });
    socket.on("round_countdown", (data) => {
      setCountDownTimer(data.seconds);
    });
    socket.on("kick_countdown", (data) => {
      setKickTimer(data.seconds);
    });
    socket.on("game_deleted", (game) => {
      if (localStorage.getItem("game_id") === game.game_id) {
        localStorage.removeItem("game_id");
      }
      navigate("/lobby");
    });
    return () => {
      socket.off("player_turn", handlePlayerTurn);
      socket.off("update_game_state");
      socket.off("round_over");
      socket.off("game_deleted");
      socket.off("kick_countdown");
    };
  }, [socket, navigate]);

  const handleOpenConfirm = (type: "leave" | "end") => {
    setActionType(type);
    setShowConfirm(true);
  };

  const handleConfirm = () => {
    if (actionType === "leave") {
      socket.emit("leave_game", { game_id: localStorage.getItem("game_id") });
      socket.emit("player_action", {
        player: user?.username,
        action: "fold",
        amount: null,
      });
      navigate("/lobby");
    } else if (actionType === "end") {
      socket.emit("delete_game", { game_id: localStorage.getItem("game_id") });
    }
    localStorage.removeItem("game_id");
    setShowConfirm(false);
  };

  useEffect(() => {
    socket.on("hand_revealed", ({ username, hand }) => {
      console.log("revealed hands:", { username, hand });
      setRevealedHands((prev) => ({
        ...prev,
        [username]: hand,
      }));
    });

    socket.on("game_started", () => {
      setRevealedHands({});
    });

    socket.on("player_kicked", () => {
      navigate("/lobby");
    });

    socket.on("player_removed", (game_id) => {
      localStorage.setItem("game_id", "");
      socket.emit("leave_room", {
        game_id,
      });
    });

    return () => {
      socket.off("hand_revealed");
      socket.off("game_started");
      socket.off("player_kicked");
      socket.off("player_removed");
    };
  }, [socket, navigate]);

  const handleShowOwnHand = () => {
    socket.emit("reveal_hand"); // backend can resolve identity via session/auth
  };

  return (
    <>
      <Container className="mt-4">
        <Row className="align-items-center justify-content-between">
          <Col xs="auto">
            {user?.username == host ? (
              <Button variant="danger" onClick={() => handleOpenConfirm("end")}>
                End Game
              </Button>
            ) : (
              <Button
                variant="danger"
                onClick={() => handleOpenConfirm("leave")}
              >
                Leave Game
              </Button>
            )}
          </Col>

          <Col xs="auto" className="ms-auto">
            {/* Modal button placed to the right, same size */}
            <HandRankModal />
          </Col>
        </Row>

        <ConfirmActionModal
          show={showConfirm}
          onClose={() => setShowConfirm(false)}
          onConfirm={handleConfirm}
          title={actionType === "end" ? "End Game?" : "Leave Game?"}
          message={
            actionType === "end"
              ? "Are you sure you want to end the game for everyone?"
              : "Are you sure you want to leave the game? You will automatically fold when action comes to you, though you may still win the pot if everyone else folds. You will not be able to join another game until this hand is over."
          }
          confirmText="Yes"
        />
      </Container>
      {gameData && <PokerGamePage gameData={gameData} />}
      {user && gameData && showRoundOver ? (
        <RoundOverOverlay
          show={showRoundOver}
          potAwards={potAwards}
          onClose={() => setShowRoundOver(false)}
          timeToNextRound={countDownTimer}
          board={gameData.board}
          revealedHands={revealedHands}
          currentUser={user.username}
          onShowOwnHand={handleShowOwnHand}
          gamePlayers={gameData.players}
        />
      ) : (
        user?.username === playerToAct &&
        gameData && (
          <PlayerActionPanel
            small_blind={gameData.blinds[0]}
            pot={gameData.pots.reduce(
              (sum, entry) => (sum = sum + entry.amount),
              0
            )}
            timeToKick={kickTimer}
            availableActions={
              actionList || [{ action: "Nothing", min: 0, allin: false }]
            }
            onActionSelect={(action: string, amount?: number) => {
              socket.emit("player_action", {
                player: user.username,
                action: action,
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
        )
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
