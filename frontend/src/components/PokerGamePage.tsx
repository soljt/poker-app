import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { PokerGameProps } from "../types";
import { useAuth } from "../context/useAuth";
import PlayingCard from "./PlayingCard";

const PokerGamePage: React.FC<PokerGameProps> = ({ gameData }) => {
  const {
    blinds,
    my_cards,
    board,
    players,
    pots,
    small_blind_player,
    big_blind_player,
    player_to_act,
    my_chips,
    phase,
  } = gameData;
  const { user } = useAuth();

  return (
    <div className="container my-4" style={{ paddingBottom: "150px" }}>
      <h2 className="text-center mb-4">Poker Game{phase && `: ${phase}`}</h2>

      <div className="row mb-4">
        <div className="col-md-4">
          <div className="card text-bg-light mb-3">
            <div className="card-header">Blinds and Chips</div>
            <div className="card-body">
              <p className="card-text">
                Small Blind: {blinds[0]} | Big Blind: {blinds[1]}
              </p>
              <p>My Chips (at the table): {my_chips}</p>
              <p>Wallet: {user?.chips}</p>
            </div>
          </div>
        </div>
        <div className="col-md-8">
          <div className="card text-bg-light mb-3">
            <div className="card-header">Players</div>
            <div className="card-body">
              <ul className="list-group list-group-flush">
                {players.map((player, index) => (
                  <li
                    key={index}
                    className={`list-group-item d-flex justify-content-between align-items-center ${
                      player.folded ? "opacity-50" : ""
                    }`}
                  >
                    <div>
                      <strong>{player.username}</strong>
                      <div className="small text-muted">
                        Bet: {player.current_bet || 0} | Chips: {player.chips}
                      </div>
                    </div>
                    <span>
                      {player.username === small_blind_player && (
                        <span className="badge bg-primary me-1">SB</span>
                      )}
                      {player.username === big_blind_player && (
                        <span className="badge bg-secondary me-1">BB</span>
                      )}
                      {player.username === player_to_act && (
                        <span className="badge bg-warning text-dark">
                          To Act
                        </span>
                      )}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-md-6">
          <div className="card text-bg-light mb-3">
            <div className="card-header">My Cards</div>
            <div className="card-body d-flex gap-2">
              {my_cards.map((card, index) => (
                <PlayingCard key={index} card={card} />
              ))}
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card text-bg-light mb-3">
            <div className="card-header">Board</div>
            <div className="card-body d-flex gap-2">
              {board.length > 0 ? (
                board.map((card, index) => (
                  <PlayingCard key={index} card={card} />
                ))
              ) : (
                <span className="text-muted">No cards on board yet</span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col">
          <div className="card text-bg-light">
            <div className="card-header">Pot</div>
            <div className="card-body">
              {pots.map((pot, index) => (
                <div
                  key={index}
                  className="border p-2 mb-3 rounded bg-white text-dark"
                >
                  <strong>
                    {index === 0 ? "Main Pot" : `Side Pot ${index}`}
                  </strong>
                  <br />
                  <strong>Amount:</strong> {pot.amount} <br />
                  <strong>Contenders:</strong> {pot.players.join(", ")}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PokerGamePage;
