import { Card, Container } from "react-bootstrap";
import PokerGamePage from "./PokerGamePage";
import { gameData } from "../constants/sampleGameData";

const GamePageGuide = () => {
  return (
    <Container>
      <h1 id="game-page-guide" className="display-3 mb-3">
        Game Page
      </h1>
      <p className="lead fs-4">
        Below is the game page you'll see after joining a game.{" "}
      </p>
      <p className="lead fs-4">
        In the top row, you see the <strong>blind amounts</strong> and your
        bankroll information, as well as the <strong>list of players</strong>{" "}
        (action flows top to bottom) with their{" "}
        <strong>chip counts and bets</strong> for the current betting round.
      </p>
      <p className="lead fs-4">
        In the next row you can see your <strong>hole cards</strong> as well as
        the <strong>board</strong>.
      </p>
      <p className="lead fs-4">
        In the bottom row you can see all <strong>pots</strong> (side pots
        included), and the list of players who have contributed (who are
        eligible to win - given that they haven't folded).
      </p>

      <Card className="h-100 shadow-sm">
        <PokerGamePage gameData={gameData} />
      </Card>
    </Container>
  );
};

export default GamePageGuide;
