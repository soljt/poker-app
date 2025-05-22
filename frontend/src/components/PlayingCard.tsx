import React from "react";

type PlayingCardProps = {
  card: string;
};

const suitColors: Record<string, string> = {
  hearts: "red",
  diamonds: "blue",
  spades: "black",
  clubs: "green",
};

const suitSymbols: Record<string, string> = {
  hearts: "♥",
  diamonds: "♦",
  spades: "♠",
  clubs: "♣",
};

const getCardInfo = (cardStr: string): { rank: string; suit: string } => {
  const [rank, , suit] = cardStr.split(" ");
  return { rank, suit };
};

const PlayingCard: React.FC<PlayingCardProps> = ({ card }) => {
  const { rank, suit } = getCardInfo(card);
  const color = suitColors[suit.toLowerCase()] || "gray";
  const symbol = suitSymbols[suit.toLowerCase()] || "?";

  return (
    <span
      className={`badge fs-3 p-2 border border-dark`}
      style={{
        backgroundColor: "white",
        color,
        minWidth: "50px",
        textAlign: "center",
        fontWeight: "bold",
      }}
    >
      {rank}
      <span className="ms-1">{symbol}</span>
    </span>
  );
};

export default PlayingCard;
