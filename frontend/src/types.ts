export interface GameData {
  blinds: [number, number];
  my_cards: string[];
  board: string[];
  players: string[];
  pots: { amount: number; players: string[] }[];
  small_blind_player: string;
  big_blind_player: string;
  player_to_act: string;
  my_bet: number;
  table_bet: number;
  my_chips: number;
}
  
  export interface PokerGameProps {
    gameData: GameData;
  }