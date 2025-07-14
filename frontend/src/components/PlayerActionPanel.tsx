import React, { useState } from "react";
import { Button, Form } from "react-bootstrap";

export interface ActionItem {
  action: string;
  min: number | null;
  allin: boolean;
}

type PlayerActionPanelProps = {
  small_blind: number;
  pot: number;
  timeToKick: number;
  availableActions: ActionItem[];
  onActionSelect: (action: string, amount?: number) => void;
  fixedPosition?: boolean;
  tableCurrentBet: number;
  playerCurrentBet: number;
};

const PlayerActionPanel: React.FC<PlayerActionPanelProps> = ({
  small_blind,
  pot,
  timeToKick,
  availableActions,
  onActionSelect,
  fixedPosition,
  tableCurrentBet,
  playerCurrentBet,
}) => {
  const [customAmount, setCustomAmount] = useState<number | null>(null);
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (!isNaN(value)) {
      setCustomAmount(value);
    }
  };

  const handleActionClick = (action: ActionItem) => {
    if (action.min !== null && !action.allin) {
      setSelectedAction(action.action);
      setCustomAmount(action.min); // default to min
    } else {
      onActionSelect(action.action, action.min ?? undefined);
    }
  };

  const handleConfirm = () => {
    if (selectedAction && customAmount) {
      onActionSelect(selectedAction, customAmount);
      setSelectedAction(null);
      setCustomAmount(null);
    }
  };

  function generateInterpolatedValues(
    pot: number,
    availableActions: ActionItem[],
    smallBlind: number
  ): number[] {
    const relevantActions = ["bet", "raise", "reraise"];

    // Find the first (and only) relevant action with a non-null min
    const relevantAction = availableActions.find(
      (a) => relevantActions.includes(a.action) && a.min !== null
    );

    if (!relevantAction || relevantAction.min === null) {
      throw new Error("No valid betting action found.");
    }

    const minValue = relevantAction.min;
    const minBound = Math.max(minValue, 0.5 * pot);
    const maxBound = Math.max(2 * pot, 2 * minValue);

    // Generate 4 linearly spaced values
    const steps = 3;
    const rawValues: number[] = [];
    for (let i = 0; i <= steps; i++) {
      const interpolated = minBound + (i * (maxBound - minBound)) / steps;
      // Round to nearest multiple of smallBlind
      const rounded = Math.round(interpolated / smallBlind) * smallBlind;
      rawValues.push(rounded);
    }

    return rawValues;
  }

  return (
    <div
      className={`${
        fixedPosition
          ? "position-fixed bottom-0 start-50 translate-middle-x"
          : ""
      } bg-light shadow p-3 rounded mb-4`}
      style={{ zIndex: 1050, minWidth: "300px" }}
    >
      <div className="text-center mb-3">
        <h5 className="fw-semibold mb-2">Your Turn</h5>

        {/* Compact Bet Info Card */}
        <div
          className="bg-white border rounded shadow-sm mx-auto mb-2"
          style={{ width: "60%", padding: "0.5rem 0.75rem" }}
        >
          <div className="d-flex justify-content-between">
            <span className="text-muted">Table Bet:</span>
            <strong>{tableCurrentBet}</strong>
          </div>
          <div className="d-flex justify-content-between">
            <span className="text-muted">Your Bet:</span>
            <strong>{playerCurrentBet}</strong>
          </div>
        </div>

        <div className="text-danger small">
          Auto-fold in <strong>{timeToKick}s</strong>
        </div>
      </div>
      <div className="d-flex flex-column gap-2 align-items-center">
        {availableActions.map((action) => (
          <div key={action.action} className="d-flex align-items-center gap-2">
            <Button
              variant="outline-primary"
              onClick={() => handleActionClick(action)}
            >
              {action.action.toUpperCase()}{" "}
              {action.allin
                ? "(All-in)"
                : action.min !== null
                ? `${action.min}+`
                : ""}
            </Button>
          </div>
        ))}

        {selectedAction && (
          <div className="w-100 mt-3">
            <Form.Group>
              <Form.Label>Enter Amount</Form.Label>
              <Form.Control
                type="number"
                step={small_blind}
                value={customAmount ?? ""}
                min={
                  availableActions.find((a) => a.action === selectedAction)
                    ?.min ?? 0
                }
                onChange={handleAmountChange}
              />
            </Form.Group>
            <div className="d-flex justify-content-between mt-2">
              {generateInterpolatedValues(
                pot,
                availableActions,
                small_blind
              ).map((amt) => (
                <Button
                  key={amt}
                  variant="outline-primary"
                  size="sm"
                  onClick={() => setCustomAmount(amt)}
                >
                  {amt}
                </Button>
              ))}
            </div>
            <Button
              variant="success"
              className="mt-2 w-100"
              onClick={handleConfirm}
              disabled={!customAmount}
            >
              Confirm {selectedAction.toUpperCase()}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerActionPanel;
