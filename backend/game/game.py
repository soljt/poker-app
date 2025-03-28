import itertools
import random
import sys
import unittest
from typing import List, Tuple, Union, Set

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
    def __init__(self, num_seats: int, players: Union[List[str], List[Player]]):
        
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

class Pot:
    def __init__(self):
        self.player_contributions = {}
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

    def award_pot(self, ranked_active_players: List[List[Player]]):
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
        print(f"------------- WITHIN POT ------------")
        print(f"splitting {self.amount} among {winners}")
        for player in winners:
            player.chips += share
            print(f"{player} gets {share}")
        print(f"-------------------------")

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

    def award_pot(self, ranked_active_players: List[List[Player]]):
        """
        Given a hand-ranked list of players, award the pot(s) to the best player(s) in it (them)
        """
        print(f"----------------------POT COLLECTION--------------------------")
        pot = self.main_pot
        while pot:         
            pot.award_pot(ranked_active_players)
            pot = pot.next
        print('-' * 80)

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
            self.table.reset()
        else:
            self.table = Table(len(players), players)
        self.deck = Deck()
        self.board = []
        self.current_bet = 0
        self.sb_amount = small_blind
        self.bb_amount = big_blind
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

    def deal_hands(self):
        """
        Deal each player 2 cards from the deck
        """
        player = self.table.sb
        for i in range(self.table.num_seats):
            player.hole_cards = self.deck.deal(2)
            player.determine_best_hand(self.board)
            print(f"{player.name} got dealt: {player.hole_cards}")
            player = player.left

        self.pot.add_contribution(self.table.sb, self.table.sb.bet(self.sb_amount)) # may be less than the SB amount
        print(f"{self.table.sb.name} is the SB, betting {self.table.sb.current_bet}")

        self.pot.add_contribution(self.table.bb, self.table.bb.bet(self.bb_amount)) # may be less than the BB amount
        print(f"{self.table.bb.name} is the BB, betting {self.table.bb.current_bet}")

        # set the current bet (may be less than BB amount)
        self.current_bet = max(self.table.sb.current_bet, self.table.bb.current_bet)
            
        print(f"POT: {self.pot}")

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

    def collect_bets(self, preflop: bool, final_round = False) -> bool:
        """
        Collect player bets
        returns: True when dealing should continue
                 False when there is no more possible action (only one remaining player can bet)
        """   
        # determine starting player and last-to-act based on placement of betting round in game (preflop vs post, headsup game vs full table)
        player, last_to_act = self.get_betting_order(preflop)

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
            if self.heads_up:
                starting_player = self.table.sb
            else:
                starting_player = self.table.bb.left
            last_to_act = self.table.bb
        else:
            if self.heads_up:
                starting_player = self.table.bb
            else:
                starting_player = self.table.sb
            last_to_act = self.table.btn
        return starting_player, last_to_act
    
    def determine_player_options(self, player: Player) -> Tuple[str, int]:
        """
        Decide which options to present to player and call prompt_player
        returns: (action: str, amount: int)
        action is a one-letter code according to self.ACTIONS
        amount is 0 for call, check, and fold
        """
        if self.current_bet > 0:
            if self.current_bet == player.current_bet: # really only happens in preflop
                return ["check", "reraise"]
            else:
                if player.chips + player.current_bet <= self.current_bet: # player doesn't have enough to raise (or possibly to call)
                    return ["call (allin)", "fold"]
                elif (len(self.active_players) - len(self.allin_players)) == 1:
                    return ["call", "fold"]
                elif player.chips + player.current_bet <= 2*self.current_bet: # player doesn't have enough to min-raise
                    return ["call", "raise (allin)", "fold"]         
                else: # player is rich
                    return ["call", "raise", "fold"]
        else: # no one has bet yet
            if player.chips < self.bb_amount:
                return ["check", "bet (allin)"]
            else:
                return ["check", "bet"]

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
        options = self.determine_player_options(player)
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

        self.deal_hands()
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
        self.deal_hands()
        self.deal_board(3)
        self.deal_board(1)
        self.deal_board(1)
        self.handle_fold(self.table.btn)
        self.handle_fold(self.table.sb) # folds the same player again in heads up...active_players will be off
        # self.collect_bets(preflop=False)
        self.rank_active_players()

class TestBettingFunctions(unittest.TestCase):

    def test_bet(self):
        player = Player('test', 500)
        self.assertEqual(player.bet(50), 50)
        self.assertEqual(player.bet(175), 125)
        self.assertEqual(player.current_bet, 175)
        self.assertEqual(player.bet(5000000), 325)

    def test_handle_bet(self):
        player1 = Player('test1', 1000)
        player2 = Player('test2', 200)
        round = PokerRound([player1, player2], 150, 300)
        round.deal_hands()
        self.assertTrue(player2.allin)
        self.assertEqual(round.pot.main_pot.amount, 350)

class TestHandRankingFunctions(unittest.TestCase):

    def test_card_sort(self):
        self.assertTrue(Card("4", "spades") < Card("K", "hearts"))

    def test_royal_flush(self):
        hand = Hand([Card("K", "spades"), Card("A", "spades"), Card("J", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand.hand_rank, 10)

        hand = Hand([Card("K", "hearts"), Card("A", "spades"), Card("J", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand.hand_rank, 5)

    def test_straight_flush(self):
        hand1 = Hand([Card("K", "diamonds"), Card("9", "diamonds"), Card("J", "diamonds"), Card("10", "diamonds"), Card("Q", "diamonds")])
        self.assertEqual(hand1.hand_rank, 9)
        self.assertEqual(hand1.card_ranks, [11])
        hand2 = Hand([Card("8", "diamonds"), Card("9", "diamonds"), Card("J", "diamonds"), Card("10", "diamonds"), Card("Q", "diamonds")])
        self.assertEqual(hand2.hand_rank, 9)
        self.assertEqual(hand2.card_ranks, [10])
        self.assertTrue(hand2 < hand1)

    def test_quads(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("10", "spades"), Card("10", "clubs")])
        self.assertEqual(hand1.hand_rank, 8)
        self.assertEqual(hand1.card_ranks, [8, 12])
        hand2 = Hand([Card("8", "diamonds"), Card("8", "hearts"), Card("8", "clubs"), Card("8", "spades"), Card("Q", "diamonds")])
        self.assertEqual(hand2.hand_rank, 8)
        self.assertEqual(hand2.card_ranks, [6, 10])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("10", "diamonds"), Card("7", "hearts"), Card("10", "hearts"), Card("10", "spades"), Card("10", "clubs")])
        self.assertEqual(hand3.hand_rank, 8)
        self.assertEqual(hand3.card_ranks, [8, 5])
        self.assertTrue(hand3 < hand1)

    def test_full_house(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("A", "spades"), Card("10", "clubs")])
        self.assertEqual(hand1.hand_rank, 7)
        self.assertEqual(hand1.card_ranks, [8, 12])
        hand2 = Hand([Card("8", "diamonds"), Card("8", "hearts"), Card("8", "clubs"), Card("Q", "spades"), Card("Q", "diamonds")])
        self.assertEqual(hand2.hand_rank, 7)
        self.assertEqual(hand2.card_ranks, [6, 10])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("10", "diamonds"), Card("7", "hearts"), Card("10", "hearts"), Card("7", "spades"), Card("10", "clubs")])
        self.assertEqual(hand3.hand_rank, 7)
        self.assertEqual(hand3.card_ranks, [8, 5])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 > hand2)

    def test_flush(self):
        hand1 = Hand([Card("K", "spades"), Card("A", "spades"), Card("5", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand1.hand_rank, 6)
        self.assertEqual(hand1.card_ranks, [12])
        hand2 = Hand([Card("K", "spades"), Card("2", "spades"), Card("J", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand2.hand_rank, 6)
        self.assertEqual(hand2.card_ranks, [11])
        self.assertTrue(hand1 > hand2)

    def test_straight(self):
        hand1 = Hand([Card("K", "hearts"), Card("A", "spades"), Card("J", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand1.hand_rank, 5)
        self.assertEqual(hand1.card_ranks, [12])
        hand2 = Hand([Card("2", "hearts"), Card("A", "spades"), Card("3", "diamonds"), Card("5", "hearts"), Card("4", "clubs")])
        self.assertEqual(hand2.hand_rank, 5)
        self.assertEqual(hand2.card_ranks, [3])
        self.assertTrue(hand1 > hand2)

    def test_trips(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("3", "spades"), Card("10", "clubs")])
        self.assertEqual(hand1.hand_rank, 4)
        self.assertEqual(hand1.card_ranks, [8, 12, 1])
        hand2 = Hand([Card("8", "diamonds"), Card("8", "hearts"), Card("8", "clubs"), Card("A", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_rank, 4)
        self.assertEqual(hand2.card_ranks, [6, 12, 0])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("10", "diamonds"), Card("7", "hearts"), Card("10", "hearts"), Card("6", "spades"), Card("10", "clubs")])
        self.assertEqual(hand3.hand_rank, 4)
        self.assertEqual(hand3.card_ranks, [8, 5, 4])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 > hand2)
    
    def test_two_pair(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("3", "spades"), Card("3", "clubs")])
        self.assertEqual(hand1.hand_rank, 3)
        self.assertEqual(hand1.card_ranks, [8, 1, 12])
        hand2 = Hand([Card("8", "diamonds"), Card("8", "hearts"), Card("A", "clubs"), Card("A", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_rank, 3)
        self.assertEqual(hand2.card_ranks, [12, 6, 0])
        self.assertTrue(hand2 > hand1)
        hand3 = Hand([Card("10", "diamonds"), Card("7", "hearts"), Card("10", "spades"), Card("3", "spades"), Card("3", "diamonds")])
        self.assertEqual(hand3.hand_rank, 3)
        self.assertEqual(hand3.card_ranks, [8, 1, 5])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 < hand2)    

    def test_pair(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("9", "spades"), Card("3", "clubs")])
        self.assertEqual(hand1.hand_rank, 2)
        self.assertEqual(hand1.card_ranks, [8, 12, 7, 1])
        hand2 = Hand([Card("8", "diamonds"), Card("5", "hearts"), Card("A", "clubs"), Card("2", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_rank, 2)
        self.assertEqual(hand2.card_ranks, [0, 12, 6, 3])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("3", "diamonds"), Card("7", "hearts"), Card("4", "spades"), Card("8", "spades"), Card("3", "hearts")])
        self.assertEqual(hand3.hand_rank, 2)
        self.assertEqual(hand3.card_ranks, [1, 6, 5, 2])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 > hand2)  
        hand4 = Hand([Card("3", "diamonds"), Card("7", "hearts"), Card("5", "spades"), Card("8", "spades"), Card("3", "hearts")])
        self.assertEqual(hand4.hand_rank, 2)
        self.assertEqual(hand4.card_ranks, [1, 6, 5, 3])
        self.assertTrue(hand3 < hand4)

    def test_high_card(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("K", "hearts"), Card("9", "spades"), Card("3", "clubs")])
        self.assertEqual(hand1.hand_rank, 1)
        self.assertEqual(hand1.card_ranks, [12, 11, 8, 7, 1])
        hand2 = Hand([Card("8", "diamonds"), Card("5", "hearts"), Card("A", "clubs"), Card("9", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_rank, 1)
        self.assertEqual(hand2.card_ranks, [12, 7, 6, 3, 0])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("3", "diamonds"), Card("7", "hearts"), Card("4", "spades"), Card("8", "spades"), Card("9", "hearts")])
        self.assertEqual(hand3.hand_rank, 1)
        self.assertEqual(hand3.card_ranks, [7, 6, 5, 2, 1])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 < hand2)  

    def test_pair_beats_high_card(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("K", "hearts"), Card("9", "spades"), Card("3", "clubs")])
        self.assertEqual(hand1.hand_rank, 1)
        self.assertEqual(hand1.card_ranks, [12, 11, 8, 7, 1])     
        hand2 = Hand([Card("8", "diamonds"), Card("5", "hearts"), Card("A", "clubs"), Card("2", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_rank, 2)
        self.assertEqual(hand2.card_ranks, [0, 12, 6, 3])
        self.assertTrue(hand2 > hand1)  

class TestDetermineWinnerFunctions(unittest.TestCase):

    def test_determine_winner(self):
        round = PokerRound(['sol', 'kenna'], 50, 100)
        round.board = [Card("K", "hearts"), Card("J", "hearts"), Card("10", "spades"), Card("Q", "spades"), Card("5", "diamonds")]
        player = round.table.btn
        player.hole_cards = [Card("A", "diamonds"), Card("6", "spades")]
        player = player.left
        player.hole_cards = [Card("A", "spades"), Card("6", "hearts")]

        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            player = player.left

        self.assertEqual(round.rank_active_players(), [[round.table.btn, round.table.bb]])

        round = PokerRound(['sol', 'kenna'], 50, 100)
        round.board = [Card("10", "hearts"), Card("Q", "spades"), Card("J", "spades"), Card("Q", "clubs"), Card("3", "clubs")]
        player = round.table.btn
        player.hole_cards = [Card("A", "diamonds"), Card("4", "hearts")]
        player = player.left
        player.hole_cards = [Card("2", "spades"), Card("7", "diamonds")]

        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            print(player.best_hand.hand_rank, ' | ', player.best_hand.card_ranks)
            player = player.left
        print(player.left.hole_cards == player.hole_cards)
        self.assertEqual(round.rank_active_players(), [[round.table.btn], [round.table.bb]])

    def test_folded_players(self):
        round = PokerRound(['sol', 'kenna', 'georg'], 50, 100)
        round.board = [Card("10", "hearts"), Card("Q", "spades"), Card("A", "spades"), Card("Q", "clubs"), Card("3", "clubs")]
        player = round.table.btn
        player.hole_cards = [Card("A", "diamonds"), Card("4", "hearts")]
        round.handle_fold(player) # folds pair of aces
        player = player.left
        player.hole_cards = [Card("2", "spades"), Card("7", "diamonds")]
        player = player.left
        player.hole_cards = [Card("10", "spades"), Card("7", "hearts")]

        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            player = player.left

        self.assertEqual(round.rank_active_players(), [[round.table.bb], [round.table.sb]])

    def test_highest_pair_wins(self):
        sol = Player("Sol", 300)
        kenna = Player("Kenna", 5000)
        louis = Player("Louis", 1000)
        beeps = Player("Beeps", 600)
        round = PokerRound([sol, kenna, louis, beeps], 25, 50)
        round.board = [Card("J", "spades"), Card("3", "hearts"), Card("8", "clubs"), Card("10", "spades"), Card("5", "diamonds")]
        sol.hole_cards = [Card("A", "diamonds"), Card("10", "hearts")]
        kenna.hole_cards = [Card("4", "clubs"), Card("9", "clubs")]
        louis.hole_cards = [Card("9", "diamonds"), Card("J", "diamonds")]
        beeps.hole_cards = [Card("8", "diamonds"), Card("Q", "hearts")]
        player = round.table.btn
        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            player = player.left

        self.assertEqual(round.rank_active_players(), [[louis], [sol], [beeps], [kenna]])

class TestPots(unittest.TestCase):
    def test_multiple_rounds(self):
        p1 = Player("P1", 19000)
        p2 = Player("P2", 500)
        p3 = Player("P3", 950)
        p4 = Player("P4", 800)
        p5 = Player("P5", 25000)
        round = PokerRound([p3, p4, p5, p1, p2], 0, 0)
        pot1 = round.pot.main_pot
        round.deal_hands()
        round.pot.add_contribution(p1, p1.bet(1000))
        round.pot.add_contribution(p2, p2.bet(500))
        self.assertEqual(pot1.player_contributions, {p4: 0, p5: 0, p1: 500, p2: 500})
        pot2 = pot1.next
        self.assertEqual(pot2.player_contributions, {p1: 500})
        round.pot.add_contribution(p3, p3.bet(950))
        round.pot.add_contribution(p4, p4.bet(800))
        round.pot.add_contribution(p5, p5.bet(2000))

        round.pot.add_contribution(p1, p1.bet(4000))
        round.pot.add_contribution(p5, p5.bet(4000))
        round.end_betting_round()

        round.deal_board(3)
        round.pot.add_contribution(p5, p5.bet(5000))
        round.pot.add_contribution(p1, p1.bet(15000))
        round.pot.add_contribution(p5, p5.bet(15000))
        round.deal_board(1)
        round.deal_board(1)
        winners = round.rank_active_players()
        round.pot.award_pot(winners)


if __name__ == "__main__":
    # unittest.main()

    # cards = Deck().cards
    # print(cards, "\n")
    # cards.sort()
    # print(cards)


    round = PokerRound([Player("Sol", 300), Player("Kenna", 5000), Player("Louis", 5000), Player("Beeps", 600)], 25, 50)
    # round.get_to_showdown()
    while True:
        round.play()
        round.table.rotate()
        round = PokerRound(round.table, 25, 50)

    # hand1 = Hand([Card("A", "diamonds"), Card("A", "diamonds")])
    # print(hand1.hand_rank)
    # print(hand1.card_ranks)    

    # deck = Deck()
    # myCards = deck.deal(2)
    # print(myCards)
    # print(deck)