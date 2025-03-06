import itertools
import random
import unittest
from typing import List, Tuple, Union

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
    HAND_RANKINGS = {10: "Royal Flush", 9: "Straight Flush", 8: "Quads", 7: "Full House", 6: "Flush", 5: "Straight", 4: "Trips", 3: "Two Pair", 2: "Pair", 1: "High Card"}
    def __init__(self, cards: List[Card], sorted=False):
        self.cards = cards
        if not sorted:
            self.cards.sort()
        self.hand_ranking, self.card_ranks = self.evaluate()

    def evaluate(self) -> Tuple[int, List[int]]:
        # check for a flush
        suit_counts = {}
        rank_counts = {}

        straight = True
        ace_low_straight = False
        prev_rank_index = Card.RANKS.index(self.cards[0].rank)
        suit_counts[self.cards[0].suit] = suit_counts.get(self.cards[0].suit, 0) + 1
        rank_counts[self.cards[0].rank] = rank_counts.get(self.cards[0].rank, 0) + 1
        for i in range(1, len(self.cards)):
            if Card.RANKS.index(self.cards[i].rank) != prev_rank_index + 1:
                if Card.RANKS.index(self.cards[i].rank) == 12 and prev_rank_index == 3: # account for ace-low straight
                    ace_low_straight = True
                else:
                    straight = False
            suit_counts[self.cards[i].suit] = suit_counts.get(self.cards[i].suit, 0) + 1
            rank_counts[self.cards[i].rank] = rank_counts.get(self.cards[i].rank, 0) + 1
            prev_rank_index = Card.RANKS.index(self.cards[i].rank)
        
        flush_suit = [i for i in suit_counts if suit_counts[i] >= 5]
        
        # royal flush
        top_card_rank_index = Card.RANKS.index(self.cards[len(self.cards)-1].rank)
        if flush_suit and straight and top_card_rank_index == Card.RANKS.index('A'):
            return (10, [])
        
        # straight flush
        if flush_suit and straight:
            if (ace_low_straight):
                return(9, [3]) # for the 5
            else:
                return (9, [top_card_rank_index])
        
        # quads
        quads_rank = [i for i in rank_counts if rank_counts[i] == 4]
        if quads_rank:
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
                return(5, [3]) # for the 5
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
        if self.hand_ranking == other.hand_ranking:
            for i in range(len(self.card_ranks)):
                if self.card_ranks[i] < other.card_ranks[i]:
                    return True
            return False
        else:
            return self.hand_ranking < other.hand_ranking
    
    def __eq__(self, other):
        if self.hand_ranking == other.hand_ranking:
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
        self.hand = []
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
    
    def fold(self):
        self.folded = True
        self.current_bet = 0

    def determine_best_hand(self, board):
        all_cards = board + self.hand
        all_cards.sort()
    
        best = None
        # generate all 5-card combinations
        for combo in itertools.combinations(all_cards, 5):
            hand = Hand(list(combo), sorted=True)
            if best is None or hand > best:
                best = hand
        self.best_hand = best

    def __repr__(self):
        return f"{self.name}"
        return f"Name: {self.name}\nChips: {self.chips}\nHand: {self.hand}\nCurrent bet: {self.current_bet}\nFolded? {'Yes' if self.folded else 'No'}"\

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

class PokerRound:
    ACTIONS = {"check": 'k', "raise": 'r', "bet": 'b', "reraise": 'rr', "call": 'c', "fold": 'f'}

    def __init__(self, players: Union[List[str], List[Player]], small_blind: int, big_blind: int):   
        self.table = Table(len(players), players)
        self.deck = Deck()
        self.pot = 0
        self.board = []
        self.current_bet = 0
        self.active_players = self.table.num_seats
        self.allin_players = 0
        self.sb_amount = small_blind
        self.bb_amount = big_blind
        self.heads_up = self.table.num_seats == 2

    def deal_hands(self):
        player = self.table.sb
        for i in range(self.table.num_seats):
            player.hand = self.deck.deal(2)
            print(f"{player.name} got dealt: {player.hand}")
            player = player.left

        self.pot += self.table.sb.bet(self.sb_amount) # may be less than the SB amount
        print(f"{self.table.sb.name} is the SB, betting {self.table.sb.current_bet}")

        self.pot += self.table.bb.bet(self.bb_amount) # may be less than the BB amount
        print(f"{self.table.bb.name} is the BB, betting {self.table.bb.current_bet}")

        # set the current bet (may be less than BB amount)
        self.current_bet = max(self.table.sb.current_bet, self.table.bb.current_bet)
            
        print(f"POT: {self.pot}")

    def deal_board(self, num_cards: int):
        self.board += self.deck.deal(num_cards)

        # get players to update their best hands
        player = self.table.btn
        for _ in range(self.table.num_seats):
            player.determine_best_hand(self.board)
            player = player.left

        # print info for new betting round
        print(f"\n\nBOARD: {self.board}\n\n")
        print(f"POT: {self.pot}")

    def collect_bets(self, preflop: bool) -> bool:
        """Collect player bets
        returns: True when dealing should continue
                 False when all players but one have folded
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
            if (self.active_players - self.allin_players) == 1 and player.current_bet == self.current_bet: 
                    return True
            
            # get the player action
            action, amount = self.get_player_action(player)

            # folded players are no longer active
            if action == self.ACTIONS["fold"]:
                self.handle_fold(player)
                if self.active_players == 1:
                    return False # all players but one have folded
            
            # handle call
            elif action == self.ACTIONS["call"]:
                self.handle_call(player)

            # handle bets
            elif action in [self.ACTIONS["raise"], self.ACTIONS["reraise"], self.ACTIONS["bet"]]:
                self.handle_raise(player, amount)
                last_to_act = player.right # used to determine when to stop looping (when everyone has called the bet)
            
            # update game state and move on to next player unless the round is over
            print(f"POT: {self.pot}")
            if player.allin:
                self.allin_players += 1
            if last_to_act == player:
                break
            player = player.left
        
        # reset bets for next betting round
        self.reset_bets()
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
    
    def get_player_action(self, player: Player) -> Tuple[str, int]:
        """
        Decide which options to present to player and call prompt_player
        returns: action: str, amount: int
        action is a one-letter code according to self.ACTIONS
        amount is 0 for call, check, and fold
        """
        if self.current_bet > 0:
            if self.current_bet == player.current_bet: # really only happens in preflop
                return self.prompt_player(player, ["check", "reraise"])
            else:
                if player.chips + player.current_bet <= self.current_bet: # player doesn't have enough to raise (or possibly to call)
                    return self.prompt_player(player, ["call (allin)", "fold"])
                elif player.chips + player.current_bet < self.current_bet + self.bb_amount: # player doesn't have enough to min-raise
                    return self.prompt_player(player, ["call", "raise (allin)", "fold"])
                else: # player is rich
                    return self.prompt_player(player, ["call", "raise", "fold"])
        else: # no one has bet yet
            if player.chips < self.bb_amount:
                return self.prompt_player(player, ["check", "bet (allin)"])
            else:
                return self.prompt_player(player, ["check", "bet"])

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
You have: {player.hand}
You may: {action_options}
Type the letter(s) corresponding to your choice: """)
        
        amount = 0
        while action not in self.ACTIONS.values():
            action = input("Invalid action. Try again: ")
        if action in ['r', 'rr', 'b']:
            # if they chose raise/bet etc. but didn't have enough to min-raise, put them all in
            if player.chips + player.current_bet < self.current_bet + self.bb_amount: 
                amount = player.chips + player.current_bet
            # otherwise, force them to raise by at least a BB
            else:
                amount = int(input('Enter the new price of poker: '))
                while amount < self.current_bet + self.bb_amount:
                    amount = int(input(f'You must raise the bet by at least one BB ({self.bb_amount}). Enter the new price of poker: '))
        return action, amount
    
    def handle_fold(self, player: Player):
        player.fold()
        self.active_players -= 1
        # DEBUG
        print(f"{player.name} now has {player.chips} and is in for {player.current_bet}. All in? {player.allin}")

    def handle_call(self, player: Player):
        # player may not have enough to call
        self.pot += player.bet(self.current_bet)
        # in case player cannot call the current bet (goes allin)
        self.current_bet = max(player.current_bet, self.current_bet) 
        # DEBUG
        print(f"{player.name} now has {player.chips} and is in for {player.current_bet}. All in? {player.allin}")

    def handle_raise(self, player: Player, amount: int):
        # player may not have enough to raise by the amount they specified
        self.pot += player.bet(amount)
        # in case player cannot raise the amount they specified (goes allin)
        self.current_bet = max(player.current_bet, self.current_bet) 
        # DEBUG
        print(f"{player.name} now has {player.chips} and is in for {player.current_bet}. All in? {player.allin}")
        
    def reset_bets(self):
        self.current_bet = 0
        player = self.table.btn
        for _ in range(self.table.num_seats):
            player.current_bet = 0
            player = player.left
            
    def determine_winner(self) -> Union[List[Player], Player]:
        """
        Determine the winning hand after the hand goes to showdown
        returns: winning_player: Player
        """
        # win without showdown
        if self.active_players == 1: 
            player = self.table.btn
            while player:
                if not player.folded:
                    player.chips += self.pot
                    show = input(f"{player.name} wins {self.pot} chips without showdown! Show? (y/n): ")
                    if show == 'y':
                        print(f"{player.name} had {player.hand}")
                    self.pot = 0
                    return player
                player = player.left
        
        else:
            # start with first non-folded player and check for royal flush, straight flush, quads, full house, flush, 
            # straight, trips, two pair, pair, high card and remember the best they have as "best hand"
            # check down to this hand strength in subsequent non-folded players and 
            # rule them out as winners if they don't beat or replace "best hand"
            best_hand = None
            winning_player = None
            tie = False
            player = self.table.btn
            for _ in range(self.table.num_seats):
                if player.folded:
                    player = player.left
                    continue
                if best_hand is None or player.best_hand > best_hand:
                    best_hand = player.best_hand
                    winning_player = player
                    tie = False
                elif best_hand == player.best_hand:
                    winning_player = [winning_player] + [player]
                    tie = True
                    
                player = player.left

            if tie:
                print("TIE!")
                print(f"{winning_player} win with {Hand.HAND_RANKINGS[winning_player[0].best_hand.hand_ranking]}!")
            else:
                print(f"{winning_player.name} wins with {Hand.HAND_RANKINGS[winning_player.best_hand.hand_ranking]}!")
                
            print(f"BOARD: {self.board}")
            player = self.table.btn
            for _ in range(self.table.num_seats):
                print(f"{player.name} makes {Hand.HAND_RANKINGS[player.best_hand.hand_ranking]} from {player.hand}")
                player = player.left
            
            return winning_player

    def play(self):
        """
        Main game loop
        """

        self.deal_hands()
        # check whether game should continue (folded out or not) after each betting round:
        if(not self.collect_bets(preflop=True)):
            self.determine_winner()
            return
        self.deal_board(3)
        if(not self.collect_bets(preflop=False)):
            self.determine_winner()
            return
        self.deal_board(1)
        if(not self.collect_bets(preflop=False)):
            self.determine_winner()
            return
        self.deal_board(1)
        self.collect_bets(preflop=False)
        self.determine_winner()

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
        self.assertEqual(round.pot, 350)

class TestHandRankingFunctions(unittest.TestCase):

    def test_card_sort(self):
        self.assertTrue(Card("4", "spades") < Card("K", "hearts"))

    def test_royal_flush(self):
        hand = Hand([Card("K", "spades"), Card("A", "spades"), Card("J", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand.hand_ranking, 10)

        hand = Hand([Card("K", "hearts"), Card("A", "spades"), Card("J", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand.hand_ranking, 5)

    def test_straight_flush(self):
        hand1 = Hand([Card("K", "diamonds"), Card("9", "diamonds"), Card("J", "diamonds"), Card("10", "diamonds"), Card("Q", "diamonds")])
        self.assertEqual(hand1.hand_ranking, 9)
        self.assertEqual(hand1.card_ranks, [11])
        hand2 = Hand([Card("8", "diamonds"), Card("9", "diamonds"), Card("J", "diamonds"), Card("10", "diamonds"), Card("Q", "diamonds")])
        self.assertEqual(hand2.hand_ranking, 9)
        self.assertEqual(hand2.card_ranks, [10])
        self.assertTrue(hand2 < hand1)

    def test_quads(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("10", "spades"), Card("10", "clubs")])
        self.assertEqual(hand1.hand_ranking, 8)
        self.assertEqual(hand1.card_ranks, [8, 12])
        hand2 = Hand([Card("8", "diamonds"), Card("8", "hearts"), Card("8", "clubs"), Card("8", "spades"), Card("Q", "diamonds")])
        self.assertEqual(hand2.hand_ranking, 8)
        self.assertEqual(hand2.card_ranks, [6, 10])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("10", "diamonds"), Card("7", "hearts"), Card("10", "hearts"), Card("10", "spades"), Card("10", "clubs")])
        self.assertEqual(hand3.hand_ranking, 8)
        self.assertEqual(hand3.card_ranks, [8, 5])
        self.assertTrue(hand3 < hand1)

    def test_full_house(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("A", "spades"), Card("10", "clubs")])
        self.assertEqual(hand1.hand_ranking, 7)
        self.assertEqual(hand1.card_ranks, [8, 12])
        hand2 = Hand([Card("8", "diamonds"), Card("8", "hearts"), Card("8", "clubs"), Card("Q", "spades"), Card("Q", "diamonds")])
        self.assertEqual(hand2.hand_ranking, 7)
        self.assertEqual(hand2.card_ranks, [6, 10])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("10", "diamonds"), Card("7", "hearts"), Card("10", "hearts"), Card("7", "spades"), Card("10", "clubs")])
        self.assertEqual(hand3.hand_ranking, 7)
        self.assertEqual(hand3.card_ranks, [8, 5])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 > hand2)

    def test_flush(self):
        hand1 = Hand([Card("K", "spades"), Card("A", "spades"), Card("5", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand1.hand_ranking, 6)
        self.assertEqual(hand1.card_ranks, [12])
        hand2 = Hand([Card("K", "spades"), Card("2", "spades"), Card("J", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand2.hand_ranking, 6)
        self.assertEqual(hand2.card_ranks, [11])
        self.assertTrue(hand1 > hand2)

    def test_straight(self):
        hand1 = Hand([Card("K", "hearts"), Card("A", "spades"), Card("J", "spades"), Card("10", "spades"), Card("Q", "spades")])
        self.assertEqual(hand1.hand_ranking, 5)
        self.assertEqual(hand1.card_ranks, [12])
        hand2 = Hand([Card("2", "hearts"), Card("A", "spades"), Card("3", "diamonds"), Card("5", "hearts"), Card("4", "clubs")])
        self.assertEqual(hand2.hand_ranking, 5)
        self.assertEqual(hand2.card_ranks, [3])
        self.assertTrue(hand1 > hand2)

    def test_trips(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("3", "spades"), Card("10", "clubs")])
        self.assertEqual(hand1.hand_ranking, 4)
        self.assertEqual(hand1.card_ranks, [8, 12, 1])
        hand2 = Hand([Card("8", "diamonds"), Card("8", "hearts"), Card("8", "clubs"), Card("A", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_ranking, 4)
        self.assertEqual(hand2.card_ranks, [6, 12, 0])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("10", "diamonds"), Card("7", "hearts"), Card("10", "hearts"), Card("6", "spades"), Card("10", "clubs")])
        self.assertEqual(hand3.hand_ranking, 4)
        self.assertEqual(hand3.card_ranks, [8, 5, 4])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 > hand2)
    
    def test_two_pair(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("3", "spades"), Card("3", "clubs")])
        self.assertEqual(hand1.hand_ranking, 3)
        self.assertEqual(hand1.card_ranks, [8, 1, 12])
        hand2 = Hand([Card("8", "diamonds"), Card("8", "hearts"), Card("A", "clubs"), Card("A", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_ranking, 3)
        self.assertEqual(hand2.card_ranks, [12, 6, 0])
        self.assertTrue(hand2 > hand1)
        hand3 = Hand([Card("10", "diamonds"), Card("7", "hearts"), Card("10", "spades"), Card("3", "spades"), Card("3", "diamonds")])
        self.assertEqual(hand3.hand_ranking, 3)
        self.assertEqual(hand3.card_ranks, [8, 1, 5])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 < hand2)    

    def test_pair(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("10", "hearts"), Card("9", "spades"), Card("3", "clubs")])
        self.assertEqual(hand1.hand_ranking, 2)
        self.assertEqual(hand1.card_ranks, [8, 12, 7, 1])
        hand2 = Hand([Card("8", "diamonds"), Card("5", "hearts"), Card("A", "clubs"), Card("2", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_ranking, 2)
        self.assertEqual(hand2.card_ranks, [0, 12, 6, 3])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("3", "diamonds"), Card("7", "hearts"), Card("4", "spades"), Card("8", "spades"), Card("3", "hearts")])
        self.assertEqual(hand3.hand_ranking, 2)
        self.assertEqual(hand3.card_ranks, [1, 6, 5, 2])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 > hand2)  
        hand4 = Hand([Card("3", "diamonds"), Card("7", "hearts"), Card("5", "spades"), Card("8", "spades"), Card("3", "hearts")])
        self.assertEqual(hand4.hand_ranking, 2)
        self.assertEqual(hand4.card_ranks, [1, 6, 5, 3])
        self.assertTrue(hand3 < hand4)

    def test_high_card(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("K", "hearts"), Card("9", "spades"), Card("3", "clubs")])
        self.assertEqual(hand1.hand_ranking, 1)
        self.assertEqual(hand1.card_ranks, [12, 11, 8, 7, 1])
        hand2 = Hand([Card("8", "diamonds"), Card("5", "hearts"), Card("A", "clubs"), Card("9", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_ranking, 1)
        self.assertEqual(hand2.card_ranks, [12, 7, 6, 3, 0])
        self.assertTrue(hand2 < hand1)
        hand3 = Hand([Card("3", "diamonds"), Card("7", "hearts"), Card("4", "spades"), Card("8", "spades"), Card("9", "hearts")])
        self.assertEqual(hand3.hand_ranking, 1)
        self.assertEqual(hand3.card_ranks, [7, 6, 5, 2, 1])
        self.assertTrue(hand3 < hand1)
        self.assertTrue(hand3 < hand2)  

    def test_pair_beats_high_card(self):
        hand1 = Hand([Card("10", "diamonds"), Card("A", "diamonds"), Card("K", "hearts"), Card("9", "spades"), Card("3", "clubs")])
        self.assertEqual(hand1.hand_ranking, 1)
        self.assertEqual(hand1.card_ranks, [12, 11, 8, 7, 1])     
        hand2 = Hand([Card("8", "diamonds"), Card("5", "hearts"), Card("A", "clubs"), Card("2", "spades"), Card("2", "diamonds")])
        self.assertEqual(hand2.hand_ranking, 2)
        self.assertEqual(hand2.card_ranks, [0, 12, 6, 3])
        self.assertTrue(hand2 > hand1)  

    def test_determine_winner(self):
        round = PokerRound(['sol', 'kenna'], 50, 100)
        round.board = [Card("K", "hearts"), Card("J", "hearts"), Card("10", "spades"), Card("Q", "spades"), Card("5", "diamonds")]
        player = round.table.btn
        player.hand = [Card("A", "diamonds"), Card("6", "spades")]
        player = player.left
        player.hand = [Card("A", "spades"), Card("6", "hearts")]

        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            player = player.left

        self.assertEqual(round.determine_winner(), [round.table.btn, round.table.bb])

        round = PokerRound(['sol', 'kenna'], 50, 100)
        round.board = [Card("10", "hearts"), Card("Q", "spades"), Card("J", "spades"), Card("Q", "clubs"), Card("3", "clubs")]
        player = round.table.btn
        player.hand = [Card("A", "diamonds"), Card("4", "hearts")]
        player = player.left
        player.hand = [Card("2", "spades"), Card("7", "diamonds")]

        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            print(player.best_hand.hand_ranking, ' | ', player.best_hand.card_ranks)
            player = player.left
        print(player.left.hand == player.hand)
        self.assertEqual(round.determine_winner(), round.table.btn)

if __name__ == "__main__":
    # unittest.main()

    # cards = Deck().cards
    # print(cards, "\n")
    # cards.sort()
    # print(cards)


    round = PokerRound([Player("Sol", 300), Player("Kenna", 5000), Player("Louis", 1000), Player("Beeps", 600)], 25, 50)
    round.play()

    # hand1 = Hand([Card("A", "diamonds"), Card("A", "diamonds")])
    # print(hand1.hand_ranking)
    # print(hand1.card_ranks)    

    # deck = Deck()
    # myCards = deck.deal(2)
    # print(myCards)
    # print(deck)