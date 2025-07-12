import React from "react";
import { Container, Row, Col, Card, Badge } from "react-bootstrap";
import PlayingCard from "./PlayingCard"; // Adjust path as needed

import { pokerHands } from "../constants/pokerHands";

const HandRankGuide: React.FC = () => {
  return (
    <Container>
      <section className="mb-5">
        <h1 className="display-3 mb-3">Hand Rankings</h1>
        <p className="lead fs-4">
          In poker, there are 5 community cards. Each player holds 2 "hole
          cards" in their hand. A player may use{" "}
          <strong>any 5-card combination of the total 7 cards</strong> to create
          their strongest hand.
        </p>
        <p className="lead fs-4">
          To win <strong>via showdown</strong>, a player must hold the
          highest-ranked 5-card hand of all the players at the table. Keep in
          mind that you don't have to make the best hand to{" "}
          <a href="#winning">win...</a>You just need everyone else to believe
          you can! That's where <a href="#betting-rounds">betting</a> comes in.
        </p>
        <p className="lead fs-4">
          All 10 possible hands are presented in order from highest-ranked to
          lowest-ranked below.
        </p>
      </section>

      {pokerHands.map((hand, index) => (
        <Card
          bg="light"
          key={index}
          className="mb-4 shadow-sm border-0 hover-shadow"
        >
          <Card.Body>
            <div className="d-flex justify-content-between align-items-center mb-2">
              <Card.Title className="h5 mb-0">{hand.title}</Card.Title>
              <Badge bg="primary" className="text-uppercase">
                #{index + 1}
              </Badge>
            </div>
            <Card.Text className="text-muted fs-5 mb-3">
              {hand.description}
            </Card.Text>
            <Row className="g-2 justify-content-center">
              {hand.cards.map((card, i) => (
                <Col key={i} xs="auto">
                  <PlayingCard card={card} />
                </Col>
              ))}
            </Row>
          </Card.Body>
        </Card>
      ))}
    </Container>
  );
};

export default HandRankGuide;
