import { Container } from "react-bootstrap";
import { mockAvailableActions, gameData } from "../constants/sampleGameData";
import DummyPlayerActionPanel from "../dummyComponents/DummyPlayerActionPanel";

const PlayerActionPanelGuide = () => {
  return (
    <Container className="py-5">
      <h1 id="action-panel-guide" className="display-3 mb-3">
        Action Panel
      </h1>
      <p className="lead fs-4">
        When it's your turn, you'll see an action panel mounted at the bottom of
        your screen. Choose your action carefully, but beware the{" "}
        <strong>kick-timer!</strong> Take too long, and you'll automatically
        fold and be removed from the table.
      </p>

      <Container className="align-center py-2" style={{ maxWidth: 500 }}>
        <DummyPlayerActionPanel
          small_blind={gameData.blinds[0]}
          pot={gameData.pots.reduce((sum, entry) => sum + entry.amount, 0)}
          timeToKick={43}
          availableActions={mockAvailableActions}
          onActionSelect={(action: string, amount?: number) => {
            console.log("Player action sent (mock):", {
              player: "You",
              action,
              amount: amount ?? null,
            });
          }}
        />
      </Container>
      <p className="lead fs-4 mb-5">
        You'll notice that you can click the raise button and choose an amount
        as you would in game. However, in a real game, <strong>raising</strong>{" "}
        has a <strong>minimum</strong> enforced by my app. You must raise by at
        least the current highest bet (essentially doubling the going rate at
        the table). In this example, the current bet must have been 50,
        necessitating that you raise it to at least 100.
      </p>
    </Container>
  );
};

export default PlayerActionPanelGuide;
