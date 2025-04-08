import React, { useState } from "react";
import { Button, Form } from "react-bootstrap";

export interface ActionItem {
  action: string;
  min: number | null;
  allin: boolean;
}

type PlayerActionPanelProps = {
  availableActions: ActionItem[];
  onActionSelect: (action: string, amount?: number) => void;
};

const PlayerActionPanel: React.FC<PlayerActionPanelProps> = ({
  availableActions,
  onActionSelect,
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

  return (
    <div
      className="position-fixed bottom-0 start-50 translate-middle-x bg-light shadow p-3 rounded mb-4"
      style={{ zIndex: 1050, minWidth: "300px" }}
    >
      <h5 className="mb-3 text-center">Your Turn</h5>
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
                ? `(${action.min}+ )`
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
                value={customAmount ?? ""}
                min={
                  availableActions.find((a) => a.action === selectedAction)
                    ?.min ?? 0
                }
                onChange={handleAmountChange}
              />
            </Form.Group>
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
