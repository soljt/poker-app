
export const gameData = {
  blinds: [10, 20] as [number, number],
  my_cards: ["A of spades", "K of spades"],
  board: ["8 of spades", "2 of hearts", "3 of spades"],
  players: [{username: "You", chips: 960, folded: false, current_bet: 40}, {username: "Villain", chips: 960, folded: false, current_bet: 0}],
  pots: [{ amount: 120, players: ["You", "Villain"] }],
  small_blind_player: "Villain",
  big_blind_player: "You",
  player_to_act: "Villain",
  available_actions: [{action: 'call', allin: false, min: null},{action: 'raise', allin: false, min: 40},{action: 'fold', allin: false, min: null}],
  my_bet: 40,
  table_bet: 40,
  my_chips: 960,
  my_wallet: 4000n,
  phase: "pre-flop",
}


export const mockPotAwards = [
  {
    winners: ["You"],
    amount: 120,
    hands: [["A of spades", "K of spades"]],
    hand_rank: "By Default",
    share: 120,
  },
];

export const mockAvailableActions = [
  { action: "fold", min: null, allin: false },
  { action: "call", min: null, allin: false },
  { action: "raise", min: 100, allin: false },
];