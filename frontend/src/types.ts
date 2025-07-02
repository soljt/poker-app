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

  export interface UserRowData {
    id: number, username: string, chips: number, role: Roles
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

  export interface LobbyEntry {
   game_id: string; 
   host: string;
   players: string[]; 
   status: string;
   queue: string[];
  }

  export enum Roles {
    player = "player",
    host = "host",
    admin = "admin"
  }

  export enum GameStatus {
    waiting_to_start = "waiting_to_start",
    between_hands = "between_hands",
    in_progress = "in_progress"
  }


    