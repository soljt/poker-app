import React from "react";
import { ListGroup, Button } from "react-bootstrap";
import { GamePlayer, PotAwardItem } from "../types";
import PlayingCard from "./PlayingCard";

type RoundOverOverlayProps = {
  show: boolean;
  potAwards: PotAwardItem[];
  onClose: () => void;
  timeToNextRound: number;
  board: string[];
  currentUser: string;
  revealedHands: Record<string, string[]>;
  onShowOwnHand: () => void;
  gamePlayers: GamePlayer[];
};

const RoundOverOverlay: React.FC<RoundOverOverlayProps> = ({
  show,
  potAwards,
  timeToNextRound,
  board,
  currentUser,
  revealedHands,
  onShowOwnHand,
  gamePlayers,
}) => {
  if (!show) return null;

  const hasRevealedOwnHand = Boolean(revealedHands[currentUser]);

  return (
    <div
      className="position-fixed top-0 start-50 translate-middle-x bg-white shadow p-3 rounded"
      style={{
        marginTop: "1rem",
        zIndex: 1050,
        maxWidth: "90%",
        width: "400px",
        border: "1px solid #ccc",
      }}
    >
      <h5 className="text-center">Round Over</h5>

      {/* Board Cards */}
      <div className="text-center mb-3">
        <strong>Board:</strong>
        <div className="mt-1">
          {board.length > 0
            ? board.map((card, index) => (
                <PlayingCard key={index} card={card} />
              ))
            : Array.from({ length: 5 }).map((_, index) => (
                <PlayingCard key={index} faceDown={true} />
              ))}
        </div>
      </div>

      {/* Pot Summary */}
      <ListGroup className="mb-3">
        {potAwards.map((pot, index) => {
          const isMainPot = index === 0;
          const isSplit = pot.winners.length > 1;
          return (
            <ListGroup.Item key={index}>
              <strong>{isMainPot ? "Main Pot" : `Side Pot ${index}`}:</strong>{" "}
              {pot.amount} chips
              <br />
              {isSplit ? (
                <>
                  Split between: {pot.winners.join(", ")}
                  <br />
                  Each gets: {pot.share} chips
                </>
              ) : (
                <>
                  Winner: {pot.winners[0]}
                  <br />
                  Amount: {pot.amount} chips
                </>
              )}
              <>
                <br />
                Winning Hand: {pot.hand_rank}
              </>
            </ListGroup.Item>
          );
        })}
      </ListGroup>

      {/* Player Hands */}
      <div className="mb-3">
        <strong>Hands:</strong>
        {gamePlayers.map((player) => (
          <div
            key={player.username}
            className="d-flex justify-content-between align-items-center border-bottom py-1"
          >
            <span>{player.username}</span>
            <span>
              {revealedHands[player.username]
                ? revealedHands[player.username].map((card, i) => (
                    <PlayingCard key={i} card={card} />
                  ))
                : [
                    <PlayingCard key="1" faceDown />,
                    <PlayingCard key="2" faceDown />,
                  ]}
            </span>
          </div>
        ))}
      </div>

      {/* Show My Hand Button */}
      {!hasRevealedOwnHand && (
        <div className="text-center mb-2">
          <Button
            variant="outline-primary"
            size="sm"
            onClick={onShowOwnHand}
            className="mb-2"
          >
            Show My Hand
          </Button>
        </div>
      )}

      <h6 className="text-center">Next round in {timeToNextRound}s</h6>
    </div>
  );
};

export default RoundOverOverlay;
