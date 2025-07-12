import LandingIntro from "../components/LandingIntro.tsx";
import HowToPlayIntro from "../components/HowToPlayIntro.tsx";
import HandRankGuide from "../components/HandRankGuide.tsx";
import BettingRoundGuide from "../components/BettingRoundGuide.tsx";
import WinningGuide from "../components/WinningGuide.tsx";
import GamePageGuide from "../components/GamePageGuide.tsx";
import PlayerActionPanelGuide from "../components/PlayerActionPanelGuide.tsx";
import RoundOverGuide from "../components/RoundOverGuide.tsx";
import LandingOutro from "../components/LandingOutro.tsx";

export default function Landing() {
  return (
    <div className={"container"} style={{ paddingBottom: "150px" }}>
      <LandingIntro />
      <HowToPlayIntro />

      <HandRankGuide />
      <BettingRoundGuide />
      <WinningGuide />

      <GamePageGuide />
      <PlayerActionPanelGuide />
      <RoundOverGuide />

      <LandingOutro />
    </div>
  );
}
