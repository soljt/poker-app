import React, { useState } from "react";
import { Modal, Button, Card } from "react-bootstrap";
import PlayingCard from "./PlayingCard";

import { pokerHands } from "../constants/pokerHands";

const HandRankModal: React.FC = () => {
  const [show, setShow] = useState(false);

  return (
    <>
      <Button variant="primary" onClick={() => setShow(true)}>
        Show Hand Rankings
      </Button>

      <Modal
        show={show}
        onHide={() => setShow(false)}
        size="lg"
        centered
        scrollable
      >
        <Modal.Header closeButton>
          <Modal.Title>Hand Rankings</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          {pokerHands.map((hand, index) => (
            <Card key={index} className="mb-4 shadow-sm">
              <Card.Body>
                <Card.Title>{hand.title}</Card.Title>
                <Card.Text className="text-muted">{hand.description}</Card.Text>
                <div className="d-flex gap-2 flex-wrap">
                  {hand.cards.map((card, i) => (
                    <PlayingCard key={i} card={card} />
                  ))}
                </div>
              </Card.Body>
            </Card>
          ))}
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default HandRankModal;
