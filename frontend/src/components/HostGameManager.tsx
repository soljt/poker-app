import { useState } from "react";
import { GameParams } from "../types";

const HostGameManager = ({
  handleCreateGame,
}: {
  handleCreateGame: (gameParams: GameParams) => void;
}) => {
  const [gameParams, setGameParams] = useState<GameParams>({
    small_blind: 10,
    big_blind: 20,
    buy_in: 1000,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setGameParams((prev) => ({
      ...prev,
      [name]: Number(value),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleCreateGame(gameParams);
  };

  return (
    <form onSubmit={handleSubmit} className="vstack gap-3">
      {[
        { label: "Small Blind:", name: "small_blind" },
        { label: "Big Blind:", name: "big_blind" },
        { label: "Buy-In:", name: "buy_in" },
      ].map(({ label, name }) => (
        <div key={name} className="d-flex align-items-center gap-3">
          <label
            htmlFor={name}
            className="form-label mb-0"
            style={{ width: 100 }}
          >
            {label}
          </label>
          <input
            className="form-control"
            type="number"
            id={name}
            name={name}
            step={name === "buy_in" ? 500 : 10}
            value={gameParams[name as keyof GameParams]}
            onChange={handleChange}
            required
          />
        </div>
      ))}

      <button className="btn btn-lg btn-info" type="submit">
        Create Game
      </button>
    </form>
  );
};

export default HostGameManager;
