import { GameStatus, LobbyEntry } from "../types";
import { User } from "../models/User";
import { Button, Card, ListGroup } from "react-bootstrap";

type Props = {
  games: LobbyEntry[];
  user: User | null;
  joinGame: (game_id: string) => void;
  deleteGame: (game_id: string, username: string) => void;
  leaveGame: (game_id: string, username: string) => void;
  handleStartGame: () => void;
  reconnectToGame: (game_id: string) => void;
};

const LobbyList: React.FC<Props> = ({
  games,
  user,
  joinGame,
  deleteGame,
  leaveGame,
  handleStartGame,
  reconnectToGame,
}) => {
  return (
    <div className="container">
      {games.length === 0 ? (
        <p className="text-center text-muted">No games available.</p>
      ) : (
        <div className="row row-cols-1 row-cols-md-2 g-4">
          {games.map((game) => (
            <div className="col" key={game.game_id}>
              <Card>
                <Card.Body>
                  <Card.Title>{game.host}'s Game</Card.Title>

                  <Card.Subtitle className="mb-1 ">
                    Small Blind: {game.small_blind}
                  </Card.Subtitle>

                  <Card.Subtitle className="mb-1 ">
                    Big Blind: {game.big_blind}
                  </Card.Subtitle>

                  <Card.Subtitle className="mb-1 ">
                    Buy-in: {game.buy_in}
                  </Card.Subtitle>

                  <Card.Subtitle className="mb-2 text-muted">
                    Game ID: {game.game_id}
                  </Card.Subtitle>

                  <Card.Subtitle className="mb-1 text-muted">
                    Status: {game.status}
                  </Card.Subtitle>

                  <Card.Subtitle className="mb-1 text-muted">
                    Players:
                  </Card.Subtitle>

                  <ListGroup className="mb-3">
                    {game.players.map((player) => (
                      <ListGroup.Item key={player}>👤 {player}</ListGroup.Item>
                    ))}
                  </ListGroup>

                  {game.joiner_queue.length >= 1 && (
                    <>
                      <Card.Subtitle className="mb-1 text-muted">
                        Queue:
                      </Card.Subtitle>

                      <ListGroup className="mb-3">
                        {game.joiner_queue.map((player) => (
                          <ListGroup.Item key={player}>
                            👤 {player}
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </>
                  )}

                  <div className="d-flex gap-2">
                    {user?.username === game.host ? (
                      <Button variant="success" onClick={handleStartGame}>
                        Start Game
                      </Button>
                    ) : (
                      !game.players.includes(user?.username || "") &&
                      !game.joiner_queue.includes(user?.username || "") && (
                        <Button
                          variant="primary"
                          onClick={() => joinGame(game.game_id)}
                        >
                          Join
                        </Button>
                      )
                    )}
                    {game.host === user?.username ? (
                      <Button
                        variant="danger"
                        onClick={() => deleteGame(game.game_id, user.username)}
                      >
                        Delete
                      </Button>
                    ) : (
                      (game.players.includes(user?.username || "") ||
                        game.joiner_queue.includes(user?.username || "")) && (
                        <Button
                          variant="outline-danger"
                          onClick={() =>
                            user?.username &&
                            leaveGame(game.game_id, user.username)
                          }
                        >
                          Leave
                        </Button>
                      )
                    )}
                    {game.players.includes(user?.username || "") &&
                      (game.status === GameStatus.in_progress ||
                        game.status === GameStatus.between_hands) && (
                        <Button
                          variant="outline-primary"
                          onClick={() => reconnectToGame(game.game_id)}
                        >
                          Reconnect
                        </Button>
                      )}
                  </div>
                </Card.Body>
              </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LobbyList;
