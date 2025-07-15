import { Card, Row, Col } from "react-bootstrap";

export default function LeaderboardRow({
  rank,
  username,
  balance,
}: {
  rank: number;
  username: string;
  balance: number;
}) {
  const balanceColor = balance >= 0 ? "text-success" : "text-danger";

  return (
    <Card className="mb-2 shadow-sm">
      <Card.Body>
        <Row className="align-items-center">
          <Col xs={2}>
            <strong>#{rank}</strong>
          </Col>
          <Col xs={6}>{username}</Col>
          <Col xs={4} className={`text-end ${balanceColor}`}>
            {balance.toLocaleString()}
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
}
