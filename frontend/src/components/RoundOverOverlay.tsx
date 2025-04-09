import React from "react";
import { Modal, ListGroup, Button } from "react-bootstrap";

import { PotAwardItem } from "../types";

type RoundOverOverlayProps = {
  show: boolean;
  potAwards: PotAwardItem[];
  onClose: () => void;
  isHost: boolean;
  onStartNextRound: () => void;
};

const RoundOverOverlay: React.FC<RoundOverOverlayProps> = ({
  show,
  potAwards,
  onClose,
  isHost,
  onStartNextRound,
}) => {
  return (
    <Modal show={show} onHide={onClose} centered backdrop="static">
      <Modal.Header closeButton>
        <Modal.Title>Round Over</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <ListGroup>
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

        {isHost && (
          <div className="d-grid mt-4">
            <Button variant="success" onClick={onStartNextRound}>
              Start Next Round
            </Button>
          </div>
        )}
      </Modal.Body>
    </Modal>
  );
};

export default RoundOverOverlay;
