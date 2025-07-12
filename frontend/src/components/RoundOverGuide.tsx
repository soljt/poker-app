import { Container } from "react-bootstrap";
import { gameData, mockPotAwards } from "../constants/sampleGameData";
import DummyRoundOverOverlay from "../dummyComponents/DummyRoundOverOverlay";
import { useState } from "react";

const RoundOverGuide = () => {
  const [revealedHands, setRevealedHands] = useState<Record<string, string[]>>(
    {}
  );
  return (
    <Container className="mb-5">
      <h1 id="round-over-guide" className="display-3 mb-3">
        End of Round Overlay
      </h1>
      <p className="lead fs-4">
        Once the round is over, you'll see an overlay like the following mounted
        at the top of your screen. Every player whose hand did not{" "}
        <strong>need</strong> to be revealed in order to claim the pot will have
        the option to show their hand to the table by clicking the "
        <strong>Show My Hand</strong>" button. Try it! Just note that once you
        show your hand, you can't hide it again...
      </p>

      <Container className="align-center py-2 mb-3" style={{ maxWidth: 500 }}>
        <DummyRoundOverOverlay
          show={true}
          potAwards={mockPotAwards}
          onClose={() => console.log("Round over modal closed")}
          timeToNextRound={8}
          board={gameData.board}
          revealedHands={revealedHands}
          currentUser="You"
          onShowOwnHand={() => setRevealedHands({ You: gameData.my_cards })}
          gamePlayers={gameData.players}
        />
      </Container>
      <p className="lead fs-4 mb-5">
        In cases where side pots must be awarded, they will also be displayed
        here. Once the timer runs out, the next hand will start.
      </p>
    </Container>
  );
};

export default RoundOverGuide;
