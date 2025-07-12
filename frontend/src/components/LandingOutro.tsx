import { Card, Col, Container, Row } from "react-bootstrap";
import { CheckIn } from "./CheckIn";

const LandingOutro = () => {
  return (
    <Container>
      <h1 className="display-2">Parting Words</h1>
      <p className="lead fs-4">
        That's it from the tutorial! Thanks for reading through it. Now get out
        there and join a table to start winning chips.
      </p>
      <CheckIn />
      <p className="lead fs-4" style={{ marginTop: 100 }}>
        P.S I asked Chat to drop you guys some tips...
      </p>
      <h2 className="h3 text-start mb-3">Tips from ChatGPT 💡</h2>
      <p className="lead text-start mb-4 fs-4">
        I didn't even ask him to overuse the em dashes...he did that on his own.
      </p>
      <Row className="g-4">
        {[
          "🧠 Think in Ranges, Not Hands – Your opponent isn’t playing a specific hand, but a range of possible hands. Try to narrow it down based on how they’ve played each street.",
          "🔍 Every Bet Tells a Story – Ask yourself what your opponent’s bet is trying to represent. Good players bet with purpose. If their story doesn’t add up, it might be a bluff.",
          "📍 Position is Profit – Acting later in a betting round gives you more information and control over the pot. Being 'in position' is a major strategic edge.",
          "🧱 Small Pots = Small Hands – Players tend to keep pots small with mediocre hands. Don’t try to bluff them out unless you see a strong opportunity.",
          "🚨 Respect the Check-Raise – A check-raise usually signals serious strength. Proceed with caution unless your hand is very strong.",
          "🔄 Don’t Auto-C-Bet – Continuation betting every flop is a common leak. If the flop hits your opponent’s range harder, checking may be better.",
          "🧊 Emotionless is Best – Avoid playing on tilt. Stay cool, calculated, and strategic, even when the cards aren’t going your way.",
          "🏃‍♂️ Play the Player – Pay attention to tendencies. Bluff less against 'calling stations' and value bet more. Against tight players, steal more often.",
          "📊 Understand Pot Odds – Know when calling is mathematically correct based on the size of the pot and your chance to improve.",
          "🧠 Fold More – Great players fold hands that average players call with. Don’t be afraid to make disciplined laydowns when something feels off.",
        ].map((tip, idx) => (
          <Col md={6} key={idx}>
            <Card bg="light" className="h-100 shadow-sm">
              <Card.Body>
                <Card.Text className="fs-5 text-muted">{tip}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default LandingOutro;
