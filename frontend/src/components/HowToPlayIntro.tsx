import { Container } from "react-bootstrap";

const HowToPlayIntro = () => {
  return (
    <Container>
      <h1 id="how-to-play" className="display-2 mb-3">
        How to Play
      </h1>
      <p className="lead fs-4">
        First, you'll find a brief rundown of the core concepts of poker. If you
        want a more extensive tutorial...you'll probably just have to google it!
        Then, we'll run through the <a href="#game-page-guide">overlay</a>{" "}
        you'll see in-game.
      </p>
    </Container>
  );
};

export default HowToPlayIntro;
