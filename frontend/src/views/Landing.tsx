import LandingIntro from "../components/LandingIntro.tsx";
import HandRankGuide from "../components/HandRankGuide.tsx";
import BettingRoundGuide from "../components/BettingRoundGuide.tsx";
import WinningGuide from "../components/WinningGuide.tsx";

export default function Landing() {
  return (
    <div className={"container"} style={{ paddingBottom: "150px" }}>
      <LandingIntro />
      <HandRankGuide />
      <BettingRoundGuide />
      <WinningGuide />
    </div>
  );
}
