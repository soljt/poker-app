import { Container } from "react-bootstrap";
import { CheckIn } from "./CheckIn";

const LandingIntro = () => {
  return (
    <Container>
      <h1 className="display-1">Welcome to poker.soljt.ch!</h1>
      <p className="lead fs-4">
        If you already know how to play poker, you can see who's playing and
        join a table right away by clicking the button below. If not, check out
        the how to play section!
      </p>

      <CheckIn />
    </Container>
  );
};

export default LandingIntro;
