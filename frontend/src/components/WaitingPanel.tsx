import React from "react";
import { LastAction } from "../types";
import { describeLastAction } from "../helpers/formatAction";

type WaitingPanelProps = {
  playerToAct: string;
  timeToKick: number | null;
  lastAction?: (LastAction & { username: string }) | null;
};

const WaitingPanel: React.FC<WaitingPanelProps> = ({
  playerToAct,
  timeToKick,
  lastAction,
}) => {
  return (
    <div
      className="position-fixed bottom-0 start-50 translate-middle-x bg-light shadow p-3 rounded mb-4 text-center"
      style={{ zIndex: 1050, minWidth: "300px" }}
    >
      {lastAction && (
        <div className="text-muted small mb-1">
          {describeLastAction(lastAction.username, lastAction)}
        </div>
      )}
      <h5 className="fw-semibold mb-0">
        Waiting for <strong>{playerToAct}</strong>...
      </h5>
      {timeToKick !== null && (
        <div className="text-danger small mt-1">
          Auto-fold in <strong>{timeToKick}s</strong>
        </div>
      )}
    </div>
  );
};

export default WaitingPanel;
