export interface GameData {
  blinds: [number, number];
  my_cards: string[];
  board: string[];
  players: string[];
  pots: { amount: number; players: string[] }[];
  small_blind_player: string;
  big_blind_player: string;
  player_to_act: string;
  available_actions: ActionItem[]
  my_bet: number;
  table_bet: number;
  my_chips: number;
  phase: string;
}
  
  export interface PokerGameProps {
    gameData: GameData;
  }

  export interface ActionItem {
    action: string, min: number | null, allin: boolean
  }
  export interface PlayerTurnData {
    player_to_act: string;
    available_actions: ActionItem[]
  }

  export interface PotAwardItem {
    winners: string[], amount: number, share: number
  }


    