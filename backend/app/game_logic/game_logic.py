import itertools
import random
import sys
from types import NoneType
import unittest
from typing import List, Tuple, Union

if __name__ == "__main__":
    from exceptions import InvalidActionError, InvalidAmountError, NotPlayersTurnError, TooManyPlayersError
else:
    from app.game_logic.exceptions import InvalidActionError, InvalidAmountError, NotPlayersTurnError, TooManyPlayersError


class Card:
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    SUITS = ["clubs", "spades", "hearts", "diamonds"]
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def __lt__(self, other):
        return self.RANKS.index(self.rank) < self.RANKS.index(other.rank)

    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Card.RANKS for suit in Card.SUITS]
        random.shuffle(self.cards)
    
    def deal(self, hand_size: int) -> List[str]:
        if len(self.cards) >= hand_size:
            return [self.cards.pop() for _ in range(hand_size)]
        else:
            raise Exception('DECK EMPTY')
        
    def __repr__(self):
        return f"{', '.join(map(str, self.cards))}"
    
class Hand:
    HAND_RANKS = {10: "Royal Flush", 9: "Straight Flush", 8: "Quads", 7: "Full House", 6: "Flush", 5: "Straight", 4: "Trips", 3: "Two Pair", 2: "Pair", 1: "High Card"}
    def __init__(self, cards: List[Card], sorted=False):
        self.cards = cards
        if not sorted:
            self.cards.sort()
        self.hand_rank, self.card_ranks = self.evaluate()

    def evaluate(self) -> Tuple[int, List[int]]:
        """
        Given a SORTED 5-card hand, determine the hand rank (see HAND_RANKS above)
        and the card ranks (used to break ties - could be kickers or top card of a flush/straight)
        Card ranks list length differs between hand ranks; high card requires 4 "kickers" whereas 
        a royal flush either wins or ties outright without looking at other cards
        returns: (hand_rank: int, card_ranks: [int])
        """
        suit_counts = {}
        rank_counts = {}

        straight = True
        ace_low_straight = False
        prev_rank_index = Card.RANKS.index(self.cards[0].rank) # for tracking straight

        suit_counts[self.cards[0].suit] = suit_counts.get(self.cards[0].suit, 0) + 1 # for tracking flush
        rank_counts[self.cards[0].rank] = rank_counts.get(self.cards[0].rank, 0) + 1 # for tracking pair, two pair, three, full house, quads

        for i in range(1, len(self.cards)):
            # track straight
            if Card.RANKS.index(self.cards[i].rank) != prev_rank_index + 1: # cards not in sequence
                if Card.RANKS.index(self.cards[i].rank) == 12 and prev_rank_index == 3: # account for ace-low straight
                    ace_low_straight = True
                else:
                    straight = False
            prev_rank_index = Card.RANKS.index(self.cards[i].rank)
            
            # track others
            suit_counts[self.cards[i].suit] = suit_counts.get(self.cards[i].suit, 0) + 1
            rank_counts[self.cards[i].rank] = rank_counts.get(self.cards[i].rank, 0) + 1
                  
        flush_suit = [i for i in suit_counts if suit_counts[i] >= 5]
        
        # royal flush
        top_card_rank_index = Card.RANKS.index(self.cards[len(self.cards)-1].rank)
        if flush_suit and straight and top_card_rank_index == Card.RANKS.index('A'):
            return (10, [])
        
        # straight flush
        if flush_suit and straight:
            if (ace_low_straight):
                return(9, [3]) # 3 is the rank index for the 5
            else:
                return (9, [top_card_rank_index])
        
        # quads
        quads_rank = [i for i in rank_counts if rank_counts[i] == 4]
        if quads_rank:
            # card_ranks is first the rank of the quads, then the rank of the kicker - the card in the hand not part of the quads
            return (8, [Card.RANKS.index(quads_rank[0])] + [Card.RANKS.index(card.rank) for card in self.cards if Card.RANKS.index(card.rank) != Card.RANKS.index(quads_rank[0])])
        
        # full house
        trips_rank = [i for i in rank_counts if rank_counts[i] == 3]
        if trips_rank:
            trips_rank = Card.RANKS.index(trips_rank[0])

        pair_ranks = [i for i in rank_counts if (rank_counts[i] == 2 and i != trips_rank)]
        if pair_ranks:
            pair_ranks = [Card.RANKS.index(pair_rank) for pair_rank in pair_ranks] # possibiliy of no trips and two pair
            pair_ranks.sort(reverse=True)

        if trips_rank and pair_ranks:
            return (7, [trips_rank, pair_ranks[0]]) # if there are trips, there can only be one pair
        
        # flush
        if flush_suit:
            return (6, [top_card_rank_index])
        
        # straight
        if straight:
            if (ace_low_straight):
                return(5, [3]) # 3 is the rank index for the 5
            else:
                return (5, [top_card_rank_index])
        
        # trips
        if trips_rank:
            return (4, [trips_rank] + list(reversed([Card.RANKS.index(card.rank) for card in self.cards if Card.RANKS.index(card.rank) != trips_rank])))
        
        # two pair
        if len(pair_ranks) == 2:
            return (3, pair_ranks + [Card.RANKS.index(card.rank) for card in self.cards if Card.RANKS.index(card.rank) not in pair_ranks])
        
        # pair
        if pair_ranks:
            return (2, [pair_ranks[0]] + list(reversed([Card.RANKS.index(card.rank) for card in self.cards if Card.RANKS.index(card.rank) != pair_ranks[0]])))
        
        # high card
        return (1, list(reversed([Card.RANKS.index(card.rank) for card in self.cards])))
           

    def __lt__(self, other):
        """
        Allows comparison using > and < between hands. Compare first the hand rank, then if that's
        not enough, compare each card rank in order
        """
        if self.hand_rank == other.hand_rank:
            for i in range(len(self.card_ranks)):
                if self.card_ranks[i] < other.card_ranks[i]:
                    return True
                elif self.card_ranks[i] > other.card_ranks[i]:
                    return False
            return False # catches equality as false
        else:
            return self.hand_rank < other.hand_rank
    
    def __eq__(self, other):
        if self.hand_rank == other.hand_rank:
            for i in range(len(self.card_ranks)):
                if self.card_ranks[i] != other.card_ranks[i]:
                    return False
            return True
        else:
            return False
    
class Player:
    def __init__(self, name: str, chips: int = 1000):
        self.name = name
        self.chips = chips
        self.hole_cards = []
        self.best_hand = None
        self.current_bet = 0
        self.playing = True
        self.folded = False
        self.allin = False
        self.left = None
        self.right = None

    def bet(self, amount: int) -> int: 
        """
        Bet the specified amount - take it from the player chips and adjust their current bet
        returns: amount ADDED to pot
        """
        # if you bet more than you have, you're all in!
        if amount > self.chips + self.current_bet:
            amount = self.chips + self.current_bet 
         
        amount_to_add_to_pot = amount - self.current_bet      
        self.chips -= amount_to_add_to_pot
        self.current_bet = amount
        if self.chips == 0:
            self.allin = True
        return amount_to_add_to_pot

    def determine_best_hand(self, board):
        """
        Player determines their own best hand based on the available board and their hole cards
        """
        all_cards = board + self.hole_cards
        all_cards.sort()
    
        best = None
        # generate all 5-card combinations
        if len(all_cards) < 5:
            self.best_hand = Hand(all_cards, sorted=True)
            return
        for combo in itertools.combinations(all_cards, 5):
            hand = Hand(list(combo), sorted=True)
            if best is None or hand > best:
                best = hand
        self.best_hand = best

    def reset(self):
        """
        Prepare player for new poker round
        """
        self.current_bet = 0
        self.folded = False
        self.allin = False
        self.best_hand = None
        self.hole_cards = []

    def __repr__(self):
        return f"{self.name}"
        return f"Name: {self.name}\nChips: {self.chips}\nHand: {self.hole_cards}\nCurrent bet: {self.current_bet}\nFolded? {'Yes' if self.folded else 'No'}"\

class Table:
    def __init__(self, num_seats: int, players: Union[List[str], List[Player]], max_seats: int=8):
        self.max_seats = max_seats
        self.num_seats = num_seats
        # if passed only a list of names, create default player instances from these names
        if isinstance(players[0], str):
            for i in range(len(players)):
                players[i] = Player(players[i])
        # heads up table
        if num_seats == 2:
            self.sb = self.btn = players[0]
            self.bb = players[1]
            self.sb.left = self.sb.right = self.bb
            self.bb.left = self.bb.right = self.sb
            return
        
        # multiway table
        old = self.btn = players[0]
        for i in range(1, len(players)):
            new = players[i]
            new.right = old
            old.left = new
            old = new
        new.left = self.btn
        self.btn.right = new

        self.sb = self.btn.left
        self.bb = self.sb.left

    def rotate(self):
        self.btn = self.btn.left
        self.sb = self.sb.left
        self.bb = self.bb.left     

    def reset(self):
        """
        Prepare for a new round of poker
        """    
        player = self.btn
        for _ in range(self.num_seats):
            player.reset()
            player = player.left

    def get_players(self) -> List[str]:
        players = []
        curr_player = self.btn
        while True:
            curr_player = curr_player.left
            players.append(str(curr_player))
            if curr_player == self.btn:
                return players
            
    def get_players_info(self) -> List[dict[str]]:
        players = []
        curr_player = self.btn
        while True:
            curr_player = curr_player.left
            players.append({
                "username": str(curr_player),
                "chips": curr_player.chips,
                "folded": curr_player.folded,
                "current_bet": curr_player.current_bet
            })
            if curr_player == self.btn:
                return players
            
    def add_player(self, player: Player) -> None:
        player.left = self.btn
        player.right = self.btn.right
        self.btn.right.left = player
        self.btn.right = player
        self.btn = player
        self.num_seats += 1

        if self.num_seats == 2:
            self.sb = player
        else:
            self.sb = player.left
            
        self.bb = self.sb.left
        
    def remove_player(self, player: Player) -> None:
        player.left.right = player.right
        player.right.left = player.left
        self.num_seats -= 1

        if self.btn == player:
            self.btn = player.left

        if self.num_seats == 2:
            self.sb = self.btn
        else:
            self.sb = self.btn.left

        self.bb = self.sb.left

class Pot:
    def __init__(self):
        self.player_contributions = {} # {player: contribution}
        self.amount = 0
        self.next = None
        self.contribution_limit = sys.maxsize # no limit until a player goes all-in
        self.max_seen_contribution = 0 # used to determine whether a pot needs to be restructured

    def add(self, player: Player, amount_to_add: int) -> int:
        """
        Add a player contribution to the pot. May not be able to add whole amount
        if pot contribution limit is set too low by an all-in player

        returns: remaining amount to be added to another pot
        """
        old_contribution = self.player_contributions.get(player, 0)

        # check whether someone with less chips is already all-in in this pot
        if old_contribution + amount_to_add > self.contribution_limit: 
            self.amount += self.contribution_limit - old_contribution
            self.player_contributions[player] = self.contribution_limit
            return amount_to_add - (self.contribution_limit - old_contribution)
        
        # can safely add the whole amount to this pot
        self.amount += amount_to_add
        self.player_contributions[player] = old_contribution + amount_to_add

        # update pot info
        if self.player_contributions[player] > self.max_seen_contribution:
            self.max_seen_contribution = self.player_contributions[player]
        if player.allin:
            self.contribution_limit = self.player_contributions[player]
        return 0

    def award_pot(self, ranked_active_players: List[List[Player]], active_players=set()) -> dict[str, list[str] | int]:
        """
        Given a hand-ranking of active players, award pot to the best-handed player(s) involved in the pot.
        """
        
        # find intersection between best_hands and current pot
        # start with the strongest group of hands (likely only one player)
        group_idx = 0
        winners = [player for player in ranked_active_players[group_idx] if player in self.player_contributions]

        # if the players with the best hand are not in this pot, repeatedly try the next group
        # AT LEAST ONE of the groups will have a player in this pot (since the union of the groups is all active players)
        while not winners:
            group_idx += 1
            winners = [player for player in ranked_active_players[group_idx] if player in self.player_contributions]
        share = self.amount // len(winners)
        amount = self.amount = share * len(winners) # skim a little off the top if the pot doesn't divide evenly
        print(f"------------- WITHIN POT ------------")
        print(f"splitting {self.amount} among {winners}")
        for player in winners:
            self.amount -= share
            player.chips += share
            print(f"{player} gets {share}")
        print(f"-------------------------")
        pot_players = set([player for player in self.player_contributions])
        hand_rank = Hand.HAND_RANKS[winners[0].best_hand.hand_rank] if len(pot_players.intersection(active_players)) != 1 else "By Default"
        return {"winners": [winner.name for winner in winners], "amount": amount, "share": share, "hand_rank": hand_rank}
    
    def refund_pot(self) -> None:
        if self.amount == 0: # pot has already been awarded or refunded
            return
        for player in self.player_contributions:
            # give the player their money back
            player.chips += self.player_contributions[player]
            self.amount -= self.player_contributions[player]
            self.player_contributions[player] = 0 # remove the money from the pot
            

    def serialize(self) -> dict[str, int | list[str]]:
        return {
            "amount": self.amount,
            "players": [str(player) for player in self.player_contributions]
        }

    def __repr__(self):
        return f"POT:\n{self.amount}\n{[(player.name, self.player_contributions[player]) for player in self.player_contributions]}"

class PotCollection:
    def __init__(self):
        self.main_pot = Pot()
        self.current_pot = self.main_pot # current pot will point to the first pot to try adding into
    
    def add_contribution(self, player: Player, amount_to_add: int):
        """
        Add a player contribution to the collection of pots. May need to be split among multiple pots
        """
        # try to add to the current pot
        pot = self.current_pot
        remainder = pot.add(player, amount_to_add)
        # check whether a side pot is created due to overflow of this bet
        while remainder:
            if not pot.next:
                pot.next = Pot()
            pot = pot.next
            remainder = pot.add(player, remainder)
        # check whether the final pot needs to be split due to this player calling all-in for less than the current bet
        if pot.max_seen_contribution > pot.contribution_limit:
            self.restructure_pot(pot)

    def restructure_pot(self, pot: Pot):
        """
        Handle the case where a player calls, but can't match the current bet and therefore goes all-in.
        The player must only be eligible to win bets up to their all-in amount, which requires "capping"
        this pot and moving bets over the all-in amount to a new side-pot
        """
        # move contributions over the contribution limit to a new pot
        temp = pot.next
        pot.next = Pot()
        pot.next.next = temp

        for player in pot.player_contributions:
            surplus = pot.player_contributions[player] - pot.contribution_limit
            if surplus > 0:
                pot.player_contributions[player] -= surplus
                pot.amount -= surplus
                pot.next.add(player, surplus)
                
        pot.max_seen_contribution = pot.contribution_limit

    def end_betting_round(self):
        """
        Handle the end of a betting round. 
        - Clean up garbage pots (created when a player bets into a 
          side pot but no one joins the action) 
        - Update the current_pot pointer to point to the pot at the 
          end of the linked list, since all new action must start
          there
        """
        prev = curr = self.current_pot
        while curr.next:
            prev = curr
            curr = curr.next

        # curr is the final pot, prev is the penultimate pot
        # if the final pot has only one member, it is due to over-contribution by a player who was not called
        # or, all who could call folded - give the player back these chips and delete the pot for the next round
        if len(curr.player_contributions) <= 1:
            print(f"COLLECTING GARBAGE:\nPOT: {curr} dies now\n")
            for player in curr.player_contributions:
                player.chips += curr.amount # refund their chips
            prev.next = None # delete curr (last pot that had only one player)
            curr = prev # prev becomes the new "last pot"
        
        self.current_pot = curr # update current pot to be the final pot after a round

    def award_pot(self, ranked_active_players: List[List[Player]], active_players=set()) -> list[dict[str, list[str] | int]]:
        """
        Given a hand-ranked list of players, award the pot(s) to the best player(s) in it (them)
        """
        print(f"----------------------POT COLLECTION--------------------------")
        pot_award_info = []
        pot = self.main_pot
        while pot:         
            pot_award_info.append(pot.award_pot(ranked_active_players, active_players))
            pot = pot.next
        print('-' * 80)
        return pot_award_info
    
    def refund_pot(self) -> None:
        pot = self.main_pot
        while pot:
            pot.refund_pot()
            pot = pot.next

    def __repr__(self):
        curr = self.main_pot
        string = ""
        while curr:
            string += curr.__repr__()
            curr = curr.next
            if curr:
                string += "\n|" * 3
                string += "\nv\n"
            
        return string

class PokerRound:
    ACTIONS = {"check": 'k', "raise": 'r', "bet": 'b', "reraise": 'rr', "call": 'c', "fold": 'f'}

    def __init__(self, players: Union[List[str], List[Player], Table], small_blind: int, big_blind: int): 
        if isinstance(players, Table):
            self.table = players
        else:
            self.table = Table(len(players), players)
        self.sb_amount = small_blind
        self.bb_amount = big_blind
        self.reset()

    def __del__(self):
        print("PokerGame object is being deleted!")

    def reset(self):
        self.table.reset()
        self.deck = Deck()
        self.board = []
        self.current_bet = 0
        self.heads_up = self.table.num_seats == 2
        self.final_betting_round_aggressor = None
        self.active_players = set()
        self.allin_players = set()
        player = self.table.btn
        # populate active player set
        for _ in range(self.table.num_seats):
            self.active_players.add(player)
            player = player.left
        self.pot = PotCollection()

        # added for interfacing with API
        self.current_player = None
        self.last_to_act = None
        self.is_betting_round_over = False
        self.phase = None
        self.is_action_finished = False
        self.is_poker_round_over = False

    # getters for API
    def get_max_seats(self) -> int:
        return self.table.max_seats

    def get_player_count(self) -> int:
        return self.table.num_seats

    # method to add new player between hands of ongoing round
    def add_player(self, player: Player) -> None:
        if self.table.num_seats == self.table.max_seats:
            raise TooManyPlayersError(self.table.max_seats)
        self.table.add_player(player)

    # method to remove leaving player between hands of ongoing round
    def remove_player(self, player: Player) -> None:
        self.table.remove_player(player)

    # helper to get a player object by username
    def get_player(self, username: str) -> Player:
        player = self.table.btn
        for _ in range(self.table.num_seats):
            if player.name == username:
                return player
            player = player.left
        return None

    def get_player_hand(self, player: str | Player) -> List[str]:
        if isinstance(player, str):
            player = self.get_player(player)
            if not player:
                return None
        return [str(card) for card in player.hole_cards]
    
    def get_pots(self) -> List[dict[str, int | List[str]]]: # [{"amount": ---, "players": [---, ---, ---]}, {...}]
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
        self.pot.refund_pot()
    
    def serialize_for_player(self, username: str) -> dict[str, List[int] | List[str] | str | List[dict[str, int | List[str]]]]:
        player = self.get_player(username)
        data = self.get_player_to_act_and_actions() if not self.is_action_finished else None
        player_to_act = data["player_to_act"] if data else None
        actions = data["available_actions"] if data else None
        return {
            "blinds": [self.sb_amount, self.bb_amount],
            "my_cards": self.get_player_hand(player),
            "board": self.get_board(),
            "players": self.table.get_players_info(), # starting from btn
            "pots": self.get_pots(),
            "small_blind_player": str(self.table.sb),
            "big_blind_player": str(self.table.bb),
            "player_to_act": player_to_act,
            "available_actions": actions,
            "my_bet": player.current_bet,
            "table_bet": self.current_bet,
            "my_chips": player.chips,
            "phase": self.phase
        }

            
    def start_round(self):
        """
        Deal the hands, extract the blinds, set the current player
        """
        # deal each player 2 cards from the deck
        player = self.table.sb
        for i in range(self.table.num_seats):
            player.hole_cards = self.deck.deal(2)
            player.determine_best_hand(self.board)
            print(f"{player.name} got dealt: {player.hole_cards}")
            player = player.left

        # extract the blinds
        self.pot.add_contribution(self.table.sb, self.table.sb.bet(self.sb_amount)) # may be less than the SB amount
        print(f"{self.table.sb.name} is the SB, betting {self.table.sb.current_bet}")

        self.pot.add_contribution(self.table.bb, self.table.bb.bet(self.bb_amount)) # may be less than the BB amount
        print(f"{self.table.bb.name} is the BB, betting {self.table.bb.current_bet}")

        # set the current bet (may be less than BB amount)
        self.current_bet = max(self.table.sb.current_bet, self.table.bb.current_bet)
            
        print(f"POT: {self.pot}")

        # set the current player and last to act
        self.phase = "preflop"
        self.current_player, self.last_to_act = self.get_betting_order(preflop=True)
        
    def get_player_to_act_and_actions(self):
        self.set_player_to_act()
        player = self.current_player
        actions = self.get_player_available_actions(player)
        return {"player_to_act": player.name, "available_actions": actions}

    def validate_player_action(self, player: Player, action: str, amount: int | None):
        if not self.current_player == player:
            raise NotPlayersTurnError(player)
        available_actions = self.get_player_available_actions(player)
        if action not in ([dic["action"] for dic in available_actions] + ["fold"]): # always allow fold - needed for player leave
            raise InvalidActionError(action)
        if amount and amount < [dic.get("min") for dic in available_actions if dic["action"] == action][0]:
            # if they chose raise/bet etc. but didn't have enough to min-raise, put them all in
            raise InvalidAmountError(amount)
        
    def apply_player_action(self, player: Player, action: str, amount: int | None):
        # folded players are no longer active
        if action == "fold":
            player.folded = True
            self.active_players.remove(player)
        
        # handle call
        elif action == "call":
            self.pot.add_contribution(player, player.bet(self.current_bet))

        # handle bets
        elif action in ["raise", "reraise", "bet"]:
            # player may not have enough to raise by the amount they specified
            self.pot.add_contribution(player, player.bet(amount))
            # in case player cannot raise the amount they specified (goes allin)
            self.current_bet = max(player.current_bet, self.current_bet) 
            self.last_to_act = player.right # used to determine when to stop looping (when everyone has called the bet)
            while self.last_to_act.folded == True:
                self.last_to_act = self.last_to_act.right
        
            # if final_round:
            #     self.final_betting_round_aggressor = player
        
        # DEBUG
        print(f"{player.name} now has {player.chips} and is in for {player.current_bet}. All in? {player.allin}")

    def update_game_state(self):
        # update game state and move on to next player unless the round is over
        print(f"POT: {self.pot}")
        if self.current_player.allin:
            self.allin_players.add(self.current_player)
        if self.last_to_act == self.current_player:
            self.is_betting_round_over = True

        # handle case where only one player is left un-folded:
        if len(self.active_players) == 1:
            self.is_betting_round_over = True
            self.is_action_finished = True # all players but one have folded
            self.is_poker_round_over = True # no need to see more cards
            return
        # handle case where all active players are all-in
        if len(self.active_players) == len(self.allin_players):
            self.is_action_finished = True
            self.is_betting_round_over = True
            return
        # handle case where all players except one are allin (non-allin player will have bet the table's current bet amount)
        if (len(self.active_players) - len(self.allin_players)) == 1 and self.active_players.difference(self.allin_players).pop().current_bet == self.current_bet: 
            self.is_action_finished = True
            self.is_betting_round_over = True
            return
        self.current_player = self.current_player.left
    
    def set_player_to_act(self):
        # start looking for the NEXT player
        player = self.current_player 
        while True: 
            # skip players who have folded or are already allin
            if (player.folded or player.allin):
                player = player.left
                continue
            
            # if they haven't folded, aren't all-in
            self.current_player = player
            break

    def start_next_phase(self):
        if self.is_action_finished or self.is_poker_round_over: # TODO handle this better
            return
        if self.phase == "preflop":
            self.deal_board(3)
            self.phase = "flop"
        elif self.phase == "flop":
            self.deal_board(1)
            self.phase = "turn"
        elif self.phase == "turn":
            self.deal_board(1)
            self.phase = "river"
        elif self.phase == "river":
            self.is_action_finished = True
            self.is_poker_round_over = True
            return
            
        self.is_betting_round_over = False
        self.current_player, self.last_to_act = self.get_betting_order(preflop=False)
        
    def handle_player_action(self, username: str, action: str, amount=None):
        try:
            # validate
            player = self.get_player(username)
            self.validate_player_action(player, action, amount) # throws exception if not
            # apply
            self.apply_player_action(player, action, amount)
            # update
            self.update_game_state()
            if self.is_betting_round_over:
                self.end_betting_round()
                self.start_next_phase()
        except Exception as e:
            raise e
        
    def end_poker_round(self): 
        """
        Called when: action is over. Must decide whether more cards must be dealt or pot can be awarded directly
        """
        if not self.is_action_finished:
            raise Exception("ACTION IS NOT FINISHED, CANNOT CALL END ROUND")
        if not self.is_poker_round_over:
            self.deal_board(5 - len(self.board))

        ranked_active_players = self.rank_active_players()
        pot_award_info = self.pot.award_pot(ranked_active_players, self.active_players)
        return pot_award_info
    
    def determine_must_show_players(self, pot_award_info):
        must_show_players = set()
        for i, pot in enumerate(pot_award_info):
            # if there's more than one winner, they all have to show
            if len(pot["winners"]) > 1:
                must_show_players = must_show_players.union(set([name for name in pot["winners"]]))
                continue
            # if there is a next (overflow) pot, the winner of this pot must show to claim it
            # or if you didn't win by default (getting folded to)
            if i+1 < len(pot_award_info) or len(self.active_players) - len(self.allin_players) > 1:
                must_show_players.add(pot["winners"][0])
        
        return [{"username": name, "hand": [str(card) for card in self.get_player(name).hole_cards]} for name in must_show_players]

    
    def start_next_round(self):
        self.table.rotate()
        self.reset()
        self.start_round()

    def deal_board(self, num_cards: int):
        """
        Deal the specified number of cards to the board
        """
        self.board += self.deck.deal(num_cards)

        # get players to update their best hands
        player = self.table.btn
        for _ in range(self.table.num_seats):
            player.determine_best_hand(self.board)
            player = player.left

        # print info for new betting round
        print(f"\n\nBOARD: {self.board}\n\n")
        print(f"POT: {self.pot}")

    def collect_bets(self, preflop: bool, final_round: bool = False) -> bool:
        """
        Collect player bets
        returns: True when dealing should continue
                 False when there is no more possible action (only one remaining player can bet)
        """   
        # determine starting player and last-to-act based on placement of betting round in game (preflop vs post, headsup game vs full table)
        # TODO will have to be done at the start of each betting round instead of here for Flask compatibility
        player, last_to_act = self.get_betting_order(preflop)
        self.current_player = player

        # loop over all players
        while True: 
            # skip players who have folded or are already allin
            if (player.folded or player.allin):
                if last_to_act == player:
                    break
                player = player.left
                continue

            # handle case where all players except one are allin (non-allin player will have bet the table's current bet amount)
            if (len(self.active_players) - len(self.allin_players)) == 1 and player.current_bet == self.current_bet: 
                    return True
            
            # get the player action
            action, amount = self.get_player_action(player)

            # folded players are no longer active
            if action == self.ACTIONS["fold"]:
                self.handle_fold(player)
                if len(self.active_players) == 1:
                    return False # all players but one have folded
            
            # handle call
            elif action == self.ACTIONS["call"]:
                self.handle_call(player)

            # handle bets
            elif action in [self.ACTIONS["raise"], self.ACTIONS["reraise"], self.ACTIONS["bet"]]:
                self.handle_raise(player, amount)
                last_to_act = player.right # used to determine when to stop looping (when everyone has called the bet)
                if final_round:
                    self.final_betting_round_aggressor = player
            
            # update game state and move on to next player unless the round is over
            print(f"POT: {self.pot}")
            if player.allin:
                self.allin_players.add(player)
            if last_to_act == player:
                break
            player = player.left
        
        # reset bets for next betting round
        self.end_betting_round()
        return True
    
    def get_betting_order(self, preflop: bool) -> Tuple[Player, Player]:
        """
        Get the betting order.
        returns: First and last players to act
        """
        if preflop:
            last_to_act = self.table.bb
            if self.heads_up:
                starting_player = self.table.sb
            else:
                starting_player = self.table.bb.left
            
        else:
            last_to_act = self.table.btn
            if self.heads_up:
                starting_player = self.table.bb
            else:
                starting_player = self.table.sb
        
        # TODO should this be somewhere else? Should "set_player_to_act" do this?
        while last_to_act.folded or last_to_act.allin:
            last_to_act = last_to_act.right
            
        return starting_player, last_to_act
    
    def get_player_available_actions(self, player: Player, min_multiplier: int=2) -> dict[str, str | int | NoneType]:
        """
        Decide which options to present to player
        returns: [{"action": str, "min": int, "allin": bool}, ...]
        """
        minimum = min_multiplier*self.current_bet
        if self.current_bet > 0:
            if self.current_bet == player.current_bet: # really only happens in preflop
                return [{"action": "check", "min": None, "allin": False}, {"action": "reraise", "min": minimum, "allin": False}]
            else:
                if player.chips + player.current_bet <= self.current_bet: # player doesn't have enough to raise (or possibly to call)
                    return [
                        {"action": "call", "min": None, "allin": True}, 
                        {"action": "fold", "min": None, "allin": False}
                        ]
                elif (len(self.active_players) - len(self.allin_players)) == 1: # player shouldn't raise - they're the only player left to act
                    return [
                        {"action": "call", "min": None, "allin": False}, 
                        {"action": "fold", "min": None, "allin": False}
                        ]
                elif player.chips + player.current_bet <= 2*self.current_bet: # player doesn't have enough to min-raise
                    return [
                        {"action": "call", "min": None, "allin": False}, 
                        {"action": "raise", "min": player.chips + player.current_bet, "allin": True}, 
                        {"action": "fold", "min": None, "allin": False}
                        ]         
                else: # player is rich
                    return [
                        {"action": "call", "min": None, "allin": False}, 
                        {"action": "raise", "min": minimum, "allin": False}, 
                        {"action": "fold", "min": None, "allin": False}
                        ]
        else: # no one has bet yet
            if player.chips < self.bb_amount: # weird case...should be CALL?
                return [
                    {"action": "check", "min": None, "allin": False}, 
                    {"action": "bet", "min": player.chips, "allin": True}
                    ]
            else:
                return [
                    {"action": "check", "min": None, "allin": False}, 
                    {"action": "bet", "min": minimum, "allin": False}
                    ]

    def prompt_player(self, player: Player, options: List[str]) -> Tuple[str, int]:
        """
        Present the player with their options and get their decision
        returns: action: str, amount: int
        action is a one-letter code according to self.ACTIONS
        amount is 0 for call, check, and fold
        """
        # format options to show one-letter codes
        action_options = " | ".join(f"{option} ('{self.ACTIONS.get(option.split(' ')[0], '?')}')" for option in options)
        action = input(f"""Player {player.name}, you have {player.chips}. The current bet is {self.current_bet} and you are in for {player.current_bet}. 
You have: {player.hole_cards}
You may: {action_options}
Type the letter(s) corresponding to your choice: """)
        
        amount = 0
        while action not in [self.ACTIONS[option.split(' ')[0]] for option in options]:
            action = input("Invalid action. Try again: ")
        if action in ['r', 'rr', 'b']:
            # if they chose raise/bet etc. but didn't have enough to min-raise, put them all in
            if player.chips + player.current_bet <= max(2*self.current_bet, self.bb_amount): 
                amount = player.chips + player.current_bet
            # otherwise, force them to raise by at least a BB
            else:
                amount = int(input('Enter the new price of poker: '))
                while amount < max(2*self.current_bet, self.bb_amount):
                    amount = int(input(f'You must bet at least {max(2*self.current_bet, self.bb_amount)}. Enter the new price of poker: '))
        return action, amount
    
    def get_player_action(self, player):
        """
        Packaged functionality for readability
        """
        options = self.get_player_available_actions(player)
        return self.prompt_player(player, options)
    
    def handle_fold(self, player: Player):
        if player.folded: # for debug purposes
            return
        player.folded = True
        self.active_players.remove(player)
        # DEBUG
        print(f"{player.name} now has {player.chips} and is in for {player.current_bet}. All in? {player.allin}")

    def handle_call(self, player: Player):
        # player may not have enough to call
        self.pot.add_contribution(player, player.bet(self.current_bet))
        # DEBUG
        print(f"{player.name} now has {player.chips} and is in for {player.current_bet}. All in? {player.allin}")

    def handle_raise(self, player: Player, amount: int):
        # player may not have enough to raise by the amount they specified
        self.pot.add_contribution(player, player.bet(amount))
        # in case player cannot raise the amount they specified (goes allin)
        self.current_bet = max(player.current_bet, self.current_bet) 
        # DEBUG
        print(f"{player.name} now has {player.chips} and is in for {player.current_bet}. All in? {player.allin}")
        
    def end_betting_round(self):
        """
        Reset player and table bets
        """
        self.current_bet = 0
        player = self.table.btn
        for _ in range(self.table.num_seats):
            player.current_bet = 0
            player = player.left
        self.pot.end_betting_round()
            
    def rank_active_players(self) -> List[List[Player]]:
        """
        Rank the players according to hand strength. Players of the same hand rank AND 
        card ranks will be grouped. Groups may consist of only one player (if only that
        player makes that hand rank and card rank(s))
        returns: [[Player]] 
        Outer list is a list of groups, inner lists are players within a group. Groups are ordered 
        strongest to weakest
        """
        ranked_active_players = []
        player = self.table.btn
        for _ in range(self.table.num_seats):
            if player.folded:
                player = player.left
                continue
            # find insertion point
            for i, group in enumerate(ranked_active_players):
                if player.best_hand > group[0].best_hand: # starting from strongest hand, player gets inserted if he beats a hand
                    ranked_active_players.insert(i, [player])
                    break
                elif player.best_hand == group[0].best_hand: # case where two players would chop
                    group.append(player)
                    break
            else:
                ranked_active_players.append([player]) # didn't beat or tie anyone (no break was hit)
            player = player.left    

        ### DEBUG ############################################
        
        print(f"RANKING: {ranked_active_players}")
        print(f"BOARD: {self.board}")
        player = self.table.btn
        for _ in range(self.table.num_seats):
            print(f"{player.name} makes {Hand.HAND_RANKS[player.best_hand.hand_rank]} from {player.hole_cards}")
            player = player.left
        ### DEBUG ############################################


        return ranked_active_players
    
    def end_round(self):
        """
        Prepare for next round of poker
        """
        # destroy the old deck and make a new one
        self.deck = Deck()
        
    def showdown(self, winning_players):
        # show cards in order
        if not self.final_betting_round_aggressor:
            player = self.table.btn.left
        else:
            player = self.final_betting_round_aggressor
        
        winner_seen = False
        for _ in range(self.table.num_seats):
            if player.folded:
                player = player.left
                continue
            if player in winning_players:
                winner_seen = True
                for player in winning_players:
                    print(f"{player.name} shows {player.hole_cards} and wins with {Hand.HAND_RANKS[winning_players[0].best_hand.hand_rank]}")
            elif winner_seen:
                if(input(f"{player.name}, will you show? (y/n): ") == 'y'):
                    print(f"{player.name} shows {player.hole_cards}")
            else:      
                print(f"{player.name} shows {player.hole_cards}")
            player = player.left

    def play(self):
        """
        Main game loop
        """

        self.start_round()
        # check whether game should continue (folded out or not) after each betting round:
        if(not self.collect_bets(preflop=True)):
            ranked_active_players = self.rank_active_players()
            self.pot.award_pot(ranked_active_players)
            return
        self.deal_board(3)
        if(not self.collect_bets(preflop=False)):
            self.rank_active_players()
            ranked_active_players = self.rank_active_players()
            self.pot.award_pot(ranked_active_players)
            return
        self.deal_board(1)
        if(not self.collect_bets(preflop=False)):
            ranked_active_players = self.rank_active_players()
            self.pot.award_pot(ranked_active_players)
            return
        self.deal_board(1)
        self.collect_bets(preflop=False, final_round=True)
        ranked_active_players = self.rank_active_players()
        self.pot.award_pot(ranked_active_players)
        # self.showdown()

    def get_to_showdown(self):
        self.start_round()
        self.deal_board(3)
        self.deal_board(1)
        self.deal_board(1)
        self.handle_fold(self.table.btn)
        self.handle_fold(self.table.sb) # folds the same player again in heads up...active_players will be off
        # self.collect_bets(preflop=False)
        self.rank_active_players()

if __name__ == "__main__":
    game = PokerRound([Player("kenna", 400), Player("hotbrian", 980), Player("soljt", 1620)], 10, 20)

    actions = ["call", "call", "reraise 450", "call", "call"]
    game.start_round()
    i = 0
    while not game.is_action_finished:
        
        if i < len(actions):
            data = game.get_player_to_act_and_actions()
            player = data["player_to_act"]
            response = actions[i].split(" ")
            if len(response) < 2:
                game.handle_player_action(player, response[0], None)
            else:
                game.handle_player_action(player, response[0], int(response[1]))
            i += 1
            continue

        data = game.get_player_to_act_and_actions()
        player = data["player_to_act"]
        actions = data["available_actions"]
        response = input(f"player {player}, you may {actions} (enter '[action] [amount | None]'):").split(" ")
        if len(response) < 2:
            game.handle_player_action(player, response[0], None)
        else:
            game.handle_player_action(player, response[0], int(response[1]))

        # for username in game.get_players():
        #     json_data = game.serialize_for_player(username)
        #     print(json_data)

    pot_award_info = game.end_poker_round()
    must_show_players = game.determine_must_show_players(pot_award_info)
    print(pot_award_info)
    print(must_show_players)


        # round.play()
        # round.table.rotate()
        # round = PokerRound(round.table, 25, 50)

    # hand1 = Hand([Card("A", "diamonds"), Card("A", "diamonds")])
    # print(hand1.hand_rank)
    # print(hand1.card_ranks)    

    # deck = Deck()
    # myCards = deck.deal(2)
    # print(myCards)
    # print(deck)