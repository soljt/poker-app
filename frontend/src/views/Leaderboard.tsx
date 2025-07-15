import { useCallback, useEffect, useState } from "react";
import { leaderboard_api } from "../services/api";
import { Col, Container, Row } from "react-bootstrap";
import LeaderboardRow from "../components/LeaderboardRow";
import { toast } from "react-toastify";

export default function Leaderboard() {
  const [users, setUsers] = useState<{ username: string; balance: number }[]>(
    []
  );

  const fetchUsers = useCallback(() => {
    leaderboard_api
      .get("/")
      .then((res) => {
        const data = res.data;
        setUsers(data.users);
      })
      .catch((err) => {
        if (err.response.status == 429) {
          toast.error(
            "I rate limited the leaderboard API to avoid database traffic...just wait a minute, then refresh."
          );
        }
      });
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <Container>
      <div className="container my-4">
        <h2 className="text-center mb-4">Leaderboard</h2>
      </div>
      <Container>
        <Row className="fw-bold bg-light border rounded py-2 px-2 mb-3 align-items-center">
          <Col xs={2}>Rank</Col>
          <Col xs={6}>Username</Col>
          <Col xs={4} className="text-end">
            Balance
          </Col>
        </Row>
      </Container>
      {users.map((u, i) => (
        <LeaderboardRow
          key={i}
          rank={i + 1}
          username={u.username}
          balance={u.balance}
        />
      ))}
    </Container>
  );
}
