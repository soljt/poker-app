import React from "react";
import { Container, Card, Row, Col } from "react-bootstrap";

const bettingRounds = [
  {
    title: "1. Pre-Flop",
    description:
      "After players receive their 2 hole cards, the first betting round begins. Players can fold, call, or raise based on their starting hand.",
  },
  {
    title: "2. Flop",
    description:
      "3 community cards are dealt face-up on the board. Another round of betting occurs, starting with the player left of (below) the dealer.",
  },
  {
    title: "3. Turn",
    description:
      "A 4th community card is dealt. Players now have more information and place their next bets accordingly.",
  },
  {
    title: "4. River",
    description:
      "The 5th and final community card is dealt. A final betting round takes place before the showdown.",
  },
];

const BettingRoundGuide: React.FC = () => {
  return (
    <Container className="py-5">
      <h1 id="betting-rounds" className="display-3 mb-3 text-start">
        Betting Rounds
      </h1>
      <p className="lead text-start mb-4 fs-4">
        Betting proceeds around the table (in our case, down the list) as each
        player chooses one of four <strong>actions</strong> on their turn:
      </p>
      <Container>
        <Row xs={1} md={2} className="g-4">
          <Col>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>Check</Card.Title>
                <Card.Text className="fs-5 text-muted">
                  Take no action. Only allowed if no bet has been made during
                  the round.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>Fold</Card.Title>
                <Card.Text className="fs-5 text-muted">
                  Discard your hand and forfeit your chance to win the pot. I
                  don't let you do this unless you're "facing action" from a
                  previous bet.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>Bet / Raise</Card.Title>
                <Card.Text className="fs-5 text-muted">
                  Bet to start the wagering or raise to increase the stakes.
                  Shows confidence in your hand.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Title>Call</Card.Title>
                <Card.Text className="fs-5 text-muted">
                  Match the current highest bet to stay in the hand and see the
                  next card or get to showdown.
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
      <Container className="py-5">
        <p className="lead text-start mb-4 fs-4">
          Poker has four <strong>betting rounds</strong>. Below is a short
          summary of each:
        </p>
        <Row className="g-4">
          {bettingRounds.map((round, index) => (
            <Col key={index} md={6}>
              <Card bg="light" className="h-100 shadow-sm">
                <Card.Body>
                  <Card.Title className="h5">{round.title}</Card.Title>
                  <Card.Text className="fs-5 text-muted">
                    {round.description}
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </Container>
    </Container>
  );
};

export default BettingRoundGuide;
