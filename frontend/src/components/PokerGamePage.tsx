import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { PokerGameProps } from "../types";
import { useAuth } from "../context/useAuth";

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
  } = gameData;
  const { user } = useAuth();

  return (
    <div className="container my-4">
      <h2 className="text-center mb-4">Poker Game</h2>

      <div className="row mb-4">
        <div className="col-md-4">
          <div className="card text-bg-light mb-3">
            <div className="card-header">Blinds</div>
            <div className="card-body">
              <p className="card-text">
                Small Blind: {blinds[0]} | Big Blind: {blinds[1]}
              </p>
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
                    className="list-group-item d-flex justify-content-between"
                  >
                    <span>{player}</span>
                    <span>
                      {player === small_blind_player && (
                        <span className="badge bg-primary me-1">SB</span>
                      )}
                      {player === big_blind_player && (
                        <span className="badge bg-secondary me-1">BB</span>
                      )}
                      {player === player_to_act && (
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
                <span key={index} className="badge bg-success fs-5 p-2">
                  {card}
                </span>
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
                  <span key={index} className="badge bg-secondary fs-5 p-2">
                    {card}
                  </span>
                ))
              ) : (
                <span className="text-muted">No cards on board yet</span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-md-6">
          <div className="card text-bg-light mb-3">
            <div className="card-header">My Stack & Bankroll</div>
            <div className="card-body">
              <p>My Chips (at the table): {gameData.my_chips}</p>
              <p>Wallet: {user?.chips}</p>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card text-bg-light mb-3">
            <div className="card-header">This Betting Round</div>
            <div className="card-body">
              <p>My Bet: {gameData.my_bet}</p>
              <p>Table Bet: {gameData.table_bet}</p>
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
                <div key={index} className="mb-2">
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
