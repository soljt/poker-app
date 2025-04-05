export interface GameData {
    blinds: [number, number];
    my_cards: string[];
    board: string[];
    players: string[];
    pots: { amount: number; players: string[] }[];
    small_blind_player: string;
    big_blind_player: string;
    player_to_act: string;
  }
  
  export interface PokerGameProps {
    gameData: GameData;
  }