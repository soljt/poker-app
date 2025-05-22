import React from "react";
import { ListGroup } from "react-bootstrap";

import { PotAwardItem } from "../types";

type RoundOverOverlayProps = {
  show: boolean;
  potAwards: PotAwardItem[];
  onClose: () => void;
};

const RoundOverOverlay: React.FC<RoundOverOverlayProps> = ({
  show,
  potAwards,
}) => {
  if (!show) return null;
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
      <ListGroup className="mb-3">
        {potAwards.map((pot, index) => {
          const isMainPot = index === 0;
          const isSplit = pot.winners.length > 1;
          return (
            <ListGroup.Item key={index}>
              <strong>
                {isMainPot ? "Main Pot" : `Side Pot ${index}`}: {pot.amount}{" "}
                chips
              </strong>
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
            </ListGroup.Item>
          );
        })}
      </ListGroup>
    </div>
  );
};

export default RoundOverOverlay;
