import random
from typing import List, Tuple

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["clubs", "spades", "hearts", "diamonds"]

class Card:
    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in RANKS for suit in SUITS]
        random.shuffle(self.cards)
    
    def deal(self, hand_size: int) -> List[str]:
        if len(self.cards) >= hand_size:
            return [self.cards.pop() for _ in range(hand_size)]
        else:
            raise Exception('DECK EMPTY')
        
    def __repr__(self):
        return f"{', '.join(map(str, self.cards))}"
    
class Player:
    def __init__(self, name: str, chips: int = 1000):
        self.name = name
        self.chips = len(name)*100
        self.hand = []
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
        if self.chips - self.current_bet < amount:
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

    def __repr__(self):
        return f"Name: {self.name}\nChips: {self.chips}\nHand: {self.hand}\nCurrent bet: {self.current_bet}\nFolded? {'Yes' if self.folded else 'No'}"\

class Table:
    def __init__(self, num_seats: int, players: List[str]):
        self.num_seats = num_seats

        # heads up table
        if num_seats == 2:
            self.sb = self.btn = Player(players[0])
            self.bb = Player(players[1])
            self.sb.left = self.sb.right = self.bb
            self.bb.left = self.bb.right = self.sb
            return
        
        # multiway table
        old = self.btn = Player(players[0])
        for i in range(1, len(players)):
            new = Player(players[i])
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

    def __init__(self, players: List[str], small_blind: int, big_blind: int):
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
        print(f"BOARD: {self.board}")
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
            
    def determine_winner(self) -> Player:
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
            print("not implemented!")
            # start with first non-folded player and check for royal flush, straight flush, quads, full house, flush, 
            # straight, trips, two pair, pair, high card and remember the best they have as "best hand"

            
            # check down to this hand strength in subsequent non-folded players and 
            # rule them out as winners if they don't beat or replace "best hand"


    def play(self):
        """
        Main game loop
        """

        self.deal_hands()
        # check whether game should continue (folded out or not)
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

if __name__ == "__main__":
    round = PokerRound(["P1", "Player2", "P3", "Player4"], 25, 50)
    round.play()
# deck = Deck()
# myCards = deck.deal(2)
# print(myCards)
# print(deck)