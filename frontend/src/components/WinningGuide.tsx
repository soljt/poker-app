import React from "react";
import { Container, Card, Row, Col } from "react-bootstrap";

const WinningGuide: React.FC = () => {
  return (
    <Container className="py-5">
      <h1 id="winning" className="display-3 mb-3 text-start">
        Winning the Round
      </h1>
      <p className="lead text-start mb-4 fs-4">
        A poker hand ends when one player remains or a showdown determines the
        strongest hand.
      </p>

      <Container className="mb-5">
        <Row className="g-4">
          <Col md={6}>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>
                  Winning by Default (everyone else folded)
                </Card.Title>
                <Card.Text className="fs-5 text-muted">
                  If all other players fold during betting, the last remaining
                  player wins the pot immediately without the need to reveal
                  their hand. You still can if you want though! Mind games...
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={6}>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>Winning by Showdown (best hand)</Card.Title>
                <Card.Text className="fs-5 text-muted">
                  When two or more players stay in until the end, a showdown
                  occurs. The winning hand is revealed, and the best 5-card hand
                  wins the pot.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      <Container className="mb-5">
        <p className="lead text-start mb-4 fs-4">
          Occasionally, the pot may be <strong>split</strong> or involve a{" "}
          <strong>side pot</strong>.
        </p>
        <Row className="g-4">
          <Col md={6}>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>Splitting the Pot</Card.Title>
                <Card.Text className="fs-5 text-muted">
                  If two or more players have identical best hands, the pot is
                  divided equally. If the pot can't be split evenly, I (the
                  house) skim the excess off the top. Thanks!
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={6}>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>Side Pots</Card.Title>
                <Card.Text className="fs-5 text-muted">
                  When a player goes all-in with fewer chips than others,
                  they're only eligible to win the main pot. Remaining players
                  can continue betting into a side pot. The all-in player cannot
                  win any part of the side pot, even if they have the best hand.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </Container>
  );
};

export default WinningGuide;
