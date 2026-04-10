from __future__ import annotations
from typing import Dict, List, Tuple, Union

from app.game_logic.exceptions import (
    InvalidActionError,
    InvalidAmountError,
    NotPlayersTurnError,
    TooManyPlayersError,
)
from app.game_logic.enums import Action, Phase
from app.game_logic.card import Card, Deck
from app.game_logic.hand import Hand, best_hand_from_cards
from app.game_logic.player import Player
from app.game_logic.table import Table
from app.game_logic.pot import PotCollection


class PokerRound:
    def __init__(
        self,
        players: Union[List[str], List[Player], Table],
        small_blind: int,
        big_blind: int,
    ) -> None:
        if isinstance(players, Table):
            self.table = players
        else:
            self.table = Table(len(players), players)
        self.sb_amount = small_blind
        self.bb_amount = big_blind
        self.reset()

    def __del__(self) -> None:
        print("PokerGame object is being deleted!")

    def reset(self) -> None:
        self.table.reset()
        self.deck = Deck()
        self.board: List[Card] = []
        self.current_bet = 0
        self.heads_up = self.table.num_seats == 2
        self.final_betting_round_aggressor = None
        self.active_players: set = set(self.table._seats)
        self.allin_players: set = set()
        self.pot = PotCollection()

        self.current_player: Player = None
        self.last_to_act: Player = None
        self.is_betting_round_over = False
        self.phase: Phase = None
        self.is_action_finished = False
        self.is_poker_round_over = False

    # ── getters for API ──────────────────────────────────────────────────────

    def get_max_seats(self) -> int:
        return self.table.max_seats

    def get_player_count(self) -> int:
        return self.table.num_seats

    def add_player(self, player: Player) -> None:
        if self.table.num_seats == self.table.max_seats:
            raise TooManyPlayersError(self.table.max_seats)
        self.table.add_player(player)

    def remove_player(self, player: Player) -> None:
        self.table.remove_player(player)

    def get_player(self, username: str) -> Player:
        return next((p for p in self.table._seats if p.name == username), None)

    def get_player_hand(self, player: Union[str, Player]) -> List[str]:
        if isinstance(player, str):
            player = self.get_player(player)
            if not player:
                return None
        return [str(card) for card in player.hole_cards]

    def get_pots(self) -> List[dict]:
        pots = []
        curr_pot = self.pot.main_pot
        while curr_pot:
            pots.append(curr_pot.serialize())
            curr_pot = curr_pot.next
        return pots

    def get_board(self) -> List[str]:
        return [str(card) for card in self.board]

    def get_players(self) -> List[str]:
        return self.table.get_players()

    def refund_pot(self) -> None:
        chip_changes = self.pot.refund_pot()
        for player, amount in chip_changes.items():
            player.chips += amount

    def serialize_for_player(self, username: str) -> dict:
        player = self.get_player(username)
        data = self.get_player_to_act_and_actions() if not self.is_action_finished else None
        player_to_act = data["player_to_act"] if data else None
        actions = data["available_actions"] if data else None
        return {
            "blinds": [self.sb_amount, self.bb_amount],
            "my_cards": self.get_player_hand(player),
            "board": self.get_board(),
            "players": self.table.get_players_info(),
            "pots": self.get_pots(),
            "small_blind_player": str(self.table.sb),
            "big_blind_player": str(self.table.bb),
            "player_to_act": player_to_act,
            "available_actions": actions,
            "my_bet": player.current_bet,
            "table_bet": self.current_bet,
            "my_chips": player.chips,
            "phase": self.phase,
        }

    # ── round lifecycle ──────────────────────────────────────────────────────

    def start_round(self) -> None:
        """Deal hole cards and post blinds."""
        player = self.table.sb
        for _ in range(self.table.num_seats):
            player.hole_cards = self.deck.deal(2)
            print(f"{player.name} got dealt: {player.hole_cards}")
            player = self.table.next_player(player)

        self.pot.add_contribution(self.table.sb, self.table.sb.bet(self.sb_amount))
        print(f"{self.table.sb.name} is the SB, betting {self.table.sb.current_bet}")
        if self.table.sb.allin:
            self.allin_players.add(self.table.sb)

        self.pot.add_contribution(self.table.bb, self.table.bb.bet(self.bb_amount))
        print(f"{self.table.bb.name} is the BB, betting {self.table.bb.current_bet}")
        if self.table.bb.allin:
            self.allin_players.add(self.table.bb)

        self.current_bet = max(self.table.sb.current_bet, self.table.bb.current_bet)

        print(f"POT: {self.pot}")
        self.phase = Phase.PREFLOP
        self.current_player, self.last_to_act = self.get_betting_order(preflop=True)

    def start_next_phase(self) -> None:
        if self.is_action_finished or self.is_poker_round_over:
            return
        if self.phase == Phase.PREFLOP:
            self.deal_board(3)
            self.phase = Phase.FLOP
        elif self.phase == Phase.FLOP:
            self.deal_board(1)
            self.phase = Phase.TURN
        elif self.phase == Phase.TURN:
            self.deal_board(1)
            self.phase = Phase.RIVER
        elif self.phase == Phase.RIVER:
            self.is_action_finished = True
            self.is_poker_round_over = True
            return

        self.is_betting_round_over = False
        self.current_player, self.last_to_act = self.get_betting_order(preflop=False)

    def end_poker_round(self) -> List[dict]:
        """
        Called when action is over. Deals remaining board cards if needed,
        ranks players, awards pots, and applies chip changes.
        """
        if not self.is_action_finished:
            raise Exception("ACTION IS NOT FINISHED, CANNOT CALL END ROUND")
        if not self.is_poker_round_over:
            self.deal_board(5 - len(self.board))

        ranked_active_players, player_hands = self.rank_active_players()
        pot_award_info, chip_changes = self.pot.award_pot(ranked_active_players, self.active_players, player_hands)
        for player, amount in chip_changes.items():
            player.chips += amount
        return pot_award_info

    def start_next_round(self) -> None:
        self.table.rotate()
        self.reset()
        self.start_round()

    def determine_must_show_players(self, pot_award_info: List[dict]) -> List[dict]:
        must_show_players = set()
        for pot in pot_award_info:
            if pot["must_show"]:
                must_show_players.update(pot["winners"])
        return [
            {"username": name, "hand": [str(c) for c in self.get_player(name).hole_cards]}
            for name in must_show_players
        ]

    # ── betting ──────────────────────────────────────────────────────────────

    def handle_player_action(self, username: str, action: str, amount=None) -> None:
        try:
            player = self.get_player(username)
            self.validate_player_action(player, action, amount)
            self.apply_player_action(player, action, amount)
            self.update_game_state()
            if self.is_betting_round_over:
                self.end_betting_round()
                self.start_next_phase()
        except Exception as e:
            raise e

    def get_player_to_act_and_actions(self) -> dict:
        self.set_player_to_act()
        player = self.current_player
        actions = self.get_player_available_actions(player)
        return {"player_to_act": player.name, "available_actions": actions}

    def validate_player_action(self, player: Player, action: str, amount: int | None) -> None:
        if not self.current_player == player:
            raise NotPlayersTurnError(player)
        available_actions = self.get_player_available_actions(player)
        if action not in ([dic["action"] for dic in available_actions] + [Action.FOLD]):
            raise InvalidActionError(action)
        if amount and amount < [dic.get("min") for dic in available_actions if dic["action"] == action][0]:
            raise InvalidAmountError(amount)

    def apply_player_action(self, player: Player, action: str, amount: int | None) -> None:
        if action == Action.FOLD:
            player.folded = True
            self.active_players.discard(player)

        elif action == Action.CALL:
            self.pot.add_contribution(player, player.bet(self.current_bet))

        elif action in (Action.RAISE, Action.RERAISE, Action.BET):
            self.pot.add_contribution(player, player.bet(amount))
            self.current_bet = max(player.current_bet, self.current_bet)
            self.last_to_act = self.table.prev_player(player)
            while self.last_to_act.folded or self.last_to_act.allin:
                self.last_to_act = self.table.prev_player(self.last_to_act)

        print(f"{player.name} now has {player.chips} and is in for {player.current_bet}. All in? {player.allin}")

    def update_game_state(self) -> None:
        print(f"POT: {self.pot}")
        if self.current_player.allin:
            self.allin_players.add(self.current_player)
        if self.last_to_act == self.current_player:
            self.is_betting_round_over = True

        if len(self.active_players) == 1:
            self.is_betting_round_over = True
            self.is_action_finished = True
            self.is_poker_round_over = True
            return
        if len(self.active_players) == len(self.allin_players):
            self.is_action_finished = True
            self.is_betting_round_over = True
            return
        if (
            (len(self.active_players) - len(self.allin_players)) == 1
            and self.active_players.difference(self.allin_players).pop().current_bet == self.current_bet
        ):
            self.is_action_finished = True
            self.is_betting_round_over = True
            return
        self.current_player = self.table.next_player(self.current_player)

    def set_player_to_act(self) -> None:
        player = self.current_player
        while True:
            if player.folded or player.allin:
                player = self.table.next_player(player)
                continue
            self.current_player = player
            break

    def end_betting_round(self) -> None:
        self.current_bet = 0
        for player in self.table._seats:
            player.current_bet = 0
        chip_changes = self.pot.end_betting_round()
        for player, amount in chip_changes.items():
            player.chips += amount

    def get_betting_order(self, preflop: bool) -> Tuple[Player, Player]:
        """Return (first_to_act, last_to_act) for this betting round."""
        if preflop:
            last_to_act = self.table.bb
            starting_player = self.table.sb if self.heads_up else self.table.next_player(self.table.bb)
        else:
            last_to_act = self.table.btn
            starting_player = self.table.bb if self.heads_up else self.table.sb

        while last_to_act.folded or last_to_act.allin:
            last_to_act = self.table.prev_player(last_to_act)

        return starting_player, last_to_act

    def get_player_available_actions(
        self, player: Player, min_multiplier: int = 2
    ) -> List[dict]:
        """Return the list of legal actions for this player."""
        minimum = min_multiplier * self.current_bet
        if self.current_bet > 0:
            if self.current_bet == player.current_bet:
                return [
                    {"action": Action.CHECK, "min": None, "allin": False},
                    {"action": Action.RERAISE, "min": minimum, "allin": False},
                ]
            else:
                if player.chips + player.current_bet <= self.current_bet:
                    return [
                        {"action": Action.CALL, "min": None, "allin": True},
                        {"action": Action.FOLD, "min": None, "allin": False},
                    ]
                elif (len(self.active_players) - len(self.allin_players)) == 1:
                    return [
                        {"action": Action.CALL, "min": None, "allin": False},
                        {"action": Action.FOLD, "min": None, "allin": False},
                    ]
                elif player.chips + player.current_bet <= 2 * self.current_bet:
                    return [
                        {"action": Action.CALL, "min": None, "allin": False},
                        {"action": Action.RAISE, "min": player.chips + player.current_bet, "allin": True},
                        {"action": Action.FOLD, "min": None, "allin": False},
                    ]
                else:
                    return [
                        {"action": Action.CALL, "min": None, "allin": False},
                        {"action": Action.RAISE, "min": minimum, "allin": False},
                        {"action": Action.FOLD, "min": None, "allin": False},
                    ]
        else:
            if player.chips < self.bb_amount:
                return [
                    {"action": Action.CHECK, "min": None, "allin": False},
                    {"action": Action.BET, "min": player.chips, "allin": True},
                ]
            else:
                return [
                    {"action": Action.CHECK, "min": None, "allin": False},
                    {"action": Action.BET, "min": minimum, "allin": False},
                ]

    def rank_active_players(self) -> Tuple[List[List[Player]], Dict[Player, Hand]]:
        """
        Rank active players by hand strength, grouping ties.
        Returns (ranked_groups, player_hands):
          - ranked_groups: [[strongest], [next], ...] strongest-first
          - player_hands: maps each non-folded Player to their best Hand
        """
        player_hands: Dict[Player, Hand] = {
            p: best_hand_from_cards(p.hole_cards + self.board)
            for p in self.table._seats if not p.folded
        }

        ranked: List[List[Player]] = []
        for player in self.table._seats:
            if player.folded:
                continue
            hand = player_hands[player]
            for i, group in enumerate(ranked):
                if hand > player_hands[group[0]]:
                    ranked.insert(i, [player])
                    break
                elif hand == player_hands[group[0]]:
                    group.append(player)
                    break
            else:
                ranked.append([player])

        print(f"RANKING: {ranked}")
        print(f"BOARD: {self.board}")
        for player, hand in player_hands.items():
            print(f"{player.name} makes {hand.hand_rank.label} from {player.hole_cards}")

        return ranked, player_hands

    # ── board / hands ────────────────────────────────────────────────────────

    def deal_board(self, num_cards: int) -> None:
        """Deal cards to the board."""
        self.board += self.deck.deal(num_cards)
        print(f"\n\nBOARD: {self.board}\n\n")
        print(f"POT: {self.pot}")

    def end_round(self) -> None:
        """Replace the deck for the next round."""
        self.deck = Deck()
