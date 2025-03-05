import random
from typing import List, Tuple

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["clubs", "spades", "hearts", "diamonds"]

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in RANKS for suit in SUITS]
        random.shuffle(self.cards)
    
    def deal(self, hand_size):
        if len(self.cards) >= hand_size:
            return [self.cards.pop() for _ in range(hand_size)]
        else:
            return []
        
    def __repr__(self):
        return f"{', '.join(map(str, self.cards))}"
    
class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.allin = False
        self.left = None
        self.right = None

    def bet(self, amount): # if you bet more than you have, you're all in!
        if self.chips - self.current_bet < amount:
            amount = self.chips + self.current_bet
        self.current_bet = amount
        self.chips -= (amount - self.current_bet)
        if self.chips == 0:
            self.allin = True
    
    def fold(self):
        self.folded = True
        self.current_bet = 0

    def __repr__(self):
        return f"Name: {self.name}\nChips: {self.chips}\nHand: {self.hand}\nCurrent bet: {self.current_bet}\nFolded? {'Yes' if self.folded else 'No'}"\

class Table:
    def __init__(self, num_seats, players):
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
    ACTIONS = {"check": 'k', "raise": 'r', "bet": 'b', "reraise": 'rr', "call": 'c'}

    def __init__(self, players, small_blind, big_blind):
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

        self.pot += self.sb_amount + self.bb_amount
        self.table.sb.bet(self.sb_amount)
        print(f"{self.table.sb.name} is the SB, betting {self.sb_amount}")

        self.table.bb.bet(self.bb_amount)
        print(f"{self.table.bb.name} is the BB, betting {self.bb_amount}")

        self.current_bet = self.bb_amount
            
        print(f"POT: {self.pot}")

    def deal_board(self, num_cards):
        self.board += self.deck.deal(num_cards)
        print(f"BOARD: {self.board}")
        print(f"POT: {self.pot}")

    def collect_bets(self, preflop):   
        player, last_to_act = self.get_betting_order(preflop)

        while True: 
            if (player.folded or player.allin):
                if last_to_act == player:
                    break
                player = player.left
                continue
            if (self.active_players - self.allin_players) == 1 and player.current_bet == self.current_bet: # no more action, deal more cards
                    return True
            while True:
                if(self.current_bet > 0):
                    if (player.current_bet < self.current_bet):
                        message = f"Player {player.name}, you have {player.chips}. The current bet is {self.current_bet}, and you are in for {player.current_bet}. Do you want to call ('c'), raise ('r'), or fold ('f')?: "
                        decision = input(message)
                        if (decision == 'f'):
                            player.fold()
                            self.active_players -= 1
                            if self.active_players == 1:
                                return False
                            break

                        elif (decision == 'c'):
                            player_in_for = player.current_bet
                            if not player.bet(self.current_bet - player_in_for):
                                print(f"Player {player.name}, calling has put you all in.")
                                player.bet(player.chips)
                                self.pot += player.chips
                            else:
                                self.pot += self.current_bet - player_in_for
                            break
                        
                        elif (decision == 'r'):
                            if (player.chips < self.current_bet + self.bb_amount):
                                print(f"Player {player.name}, raising has put you all in.")
                                amount = player.chips
                                player.bet(amount)
                            else:
                                amount = int(input(f"Player {player.name}, how much would you like to raise?: "))
                                if amount < self.current_bet + self.bb_amount:
                                    print(f"Player {player.name}, you must raise by at least {self.bb_amount}.")
                                    continue
                                elif not player.bet(amount):
                                    print(f"Player {player.name}, you only have {player.chips}.")
                                    continue
                            self.pot += amount
                            self.current_bet = amount
                            last_to_act = player.right
                            break
                    else:
                        message = f"Player {player.name}, you have {player.chips}. The current bet is {self.current_bet}, and you are in for {player.current_bet}. Do you want to check ('k') or re-raise ('rr')?: "
                        decision = input(message)
                        if (decision == 'k'):
                            break
                        elif (decision == 'rr'):
                            if (player.chips < self.current_bet + self.bb_amount):
                                print(f"Player {player.name}, you don't have enough to min-raise, so you're all in.")
                                amount = player.chips
                                player.bet(amount)
                            else:
                                amount = int(input(f"Player {player.name}, how much would you like to reraise?: "))
                                if amount < self.current_bet + self.bb_amount:
                                    print(f"Player {player.name}, you must reraise by at least {self.bb_amount}.")
                                    continue
                                elif not player.bet(amount):
                                    print(f"Player {player.name}, you only have {player.chips}.")
                                    continue
                            self.pot += amount
                            self.current_bet = amount
                            last_to_act = player.right
                            break
                else:
                    message = f"Player {player.name}, you have {player.chips}. No one has bet yet. Do you want to check ('k') or bet ('b')?: "
                    decision = input(message)
                    if (decision == 'k'):
                        break
                    elif (decision == 'b'):
                        if (player.chips < self.current_bet + self.bb_amount):
                            print(f"Player {player.name}, you don't have enough to min-bet, so you're all in.")
                            amount = player.chips
                            player.bet(player.chips)
                        else:
                            amount = int(input(f"Player {player.name}, how much would you like to bet?: "))
                            if amount < self.current_bet + self.bb_amount:
                                print(f"Player {player.name}, you must bet at least {self.bb_amount}.")
                                continue
                            elif not player.bet(amount):
                                print(f"Player {player.name}, you only have {player.chips}.")
                                continue
                        self.pot += amount
                        self.current_bet = amount
                        last_to_act = player.right
                        break
            print(f"POT: {self.pot}")
            if player.allin:
                self.allin_players += 1
            if last_to_act == player:
                break
            player = player.left
        self.current_bet = 0
        for _ in range(self.table.num_seats):
            player.current_bet = 0
            player = player.left
        return True
    
    def get_betting_order(self, preflop):
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
    
    def get_player_action(self, player: Player):
        if self.current_bet > 0:
            if self.current_bet == player.current_bet:
                self.prompt_player(player, ["check", "reraise"])
            else:
                if player.chips + player.current_bet < self.current_bet:
                    self.prompt_player(player, ["call (allin)", "fold"])
                elif player.chips + player.current_bet < self.current_bet + self.bb_amount:
                    self.prompt_player(player, ["call", "raise (allin)", "fold"])
                else:
                    self.prompt_player(player, ["call", "raise", "fold"])
        else:
            self.prompt_player(player, ["check", "bet"])

    def prompt_player(self, player: Player, options: List[str]) -> Tuple[str, int]:
        action = input(f"""Player {player.name}, you have {player.chips}. The current bet is {self.current_bet} 
                       and you are in for {player.current_bet}. You may: {'|' + option + " ('" + self.ACTIONS[option.split(' ')[0]] + "')" } '|'\n
                       Type the letter(s) corresponding to your choice: """ for option in options)
        amount = 0
        while action not in self.ACTIONS.items:
            input("Invalid action. Try again: ")
        if action in ['r', 'rr', 'b']:
            if player.chips + player.current_bet < self.current_bet + self.bb_amount: # if they chose raise/bet etc. but didn't have enough to min-raise
                amount = player.chips + player.current_bet
            else:
                amount = int(input('Enter the new price of poker: '))
                while amount < self.current_bet + self.bb_amount:
                    amount = int(input(f'You must raise the bet by at least one BB ({self.bb_amount}). Enter the new price of poker: '))
        return action, amount
    
    def handle_fold(self, player: Player):
        player.fold()
        self.active_players -= 1

    def handle_call(self, player: Player):
        self.pot += self.current_bet - player.current_bet
        player.bet(self.current_bet)

    def handle_raise(self, player: Player, amount: int):
        player_prev_bet = player.current_bet
        player.bet(amount)
        self.pot += player.current_bet - player_prev_bet

    def reset_bets(self):
        self.current_bet = 0
        player = self.table.btn
        for _ in range(self.table.num_seats):
            player.current_bet = 0
            player = player.left
            
    def determine_winner(self):
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
                    return
                player = player.left
        
        else:
            print("not implemented!")
            # start with first non-folded player and check for royal flush, straight flush, quads, full house, flush, 
            # straight, trips, two pair, pair, high card and remember the best they have as "best hand"
            
            
            # check down to this hand strength in subsequent non-folded players and 
            # rule them out as winners if they don't beat or replace "best hand"


    def play(self):
        self.deal_hands()
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
        self.determine_winner()

if __name__ == "__main__":
    round = PokerRound(["Kenna", "Sol", "Louis"], 25, 50)
    round.play()
# deck = Deck()
# myCards = deck.deal(2)
# print(myCards)
# print(deck)