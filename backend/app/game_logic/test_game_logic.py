from game_logic import Player, PokerRound, Hand, Card
import unittest

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
        round.start_round()
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
        round.start_round()
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

class TestDetermineShowers(unittest.TestCase):
    def test_split_pot(self):
        round = PokerRound(['sol', 'kenna'], 50, 100)
        round.start_round()
        round.board = [Card("J", "hearts"), Card("J", "diamonds"), Card("5", "hearts"), Card("Q", "clubs"), Card("5", "diamonds")]
        player = round.table.btn
        player.hole_cards = [Card("4", "clubs"), Card("7", "hearts")]
        player = player.left
        player.hole_cards = [Card("10", "clubs"), Card("3", "diamonds")]

        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            player = player.left

        ranked_active_players = round.rank_active_players()
        pot_award_info = round.pot.award_pot(ranked_active_players)
        self.assertEqual(set([entry["username"] for entry in round.determine_must_show_players(pot_award_info)]), set(["sol", "kenna"]))

    def test_allin_player_loss(self):
        p1 = Player("soljt", 19000)
        p2 = Player("kenna", 500)
        round = PokerRound([p1, p2], 10, 20)

        # start game
        round.start_round()
        player = round.table.btn
        player.hole_cards = [Card("J", "clubs"), Card("6", "diamonds")]
        player = player.left
        player.hole_cards = [Card("K", "clubs"), Card("Q", "diamonds")]
        print(round.get_player_to_act_and_actions())


        # loop here
        actions_sequence = [{"username": "soljt", "action": "raise", "amount": 200}, 
         {"username": "kenna", "action": "call", "amount": None},
         {"username": "kenna", "action": "bet", "amount": 300},
         {"username": "soljt", "action": "call", "amount": None}]
        i=0
        while not round.is_action_finished:
            action = actions_sequence[i]
            round.handle_player_action(action["username"], action["action"], action["amount"])
            round.get_player_to_act_and_actions()
            i+=1
        round.board = [Card("6", "hearts"), Card("K", "diamonds"), Card("Q", "hearts"), Card("6", "clubs"), Card("5", "clubs")]
        
        # get players to update their best hands
        player = round.table.btn
        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            player = player.left
        
        pot_award_info = round.end_poker_round()
        must_show = round.determine_must_show_players(pot_award_info)
        self.assertEqual(set([entry["username"] for entry in must_show]), set(["soljt"]))

class TestShowWinningHand(unittest.TestCase):
    def test_side_pot(self):
        p1 = Player("P1", 19000)
        p2 = Player("P2", 500)
        p3 = Player("P3", 950)
        round = PokerRound([p1, p2, p3], 0, 0)
        round.start_round()
        round.board = [Card("J", "hearts"), Card("J", "diamonds"), Card("5", "hearts"), Card("Q", "clubs"), Card("5", "diamonds")]
        player = round.table.btn
        player.hole_cards = [Card("J", "clubs"), Card("7", "hearts")]
        player = player.left
        player.hole_cards = [Card("10", "clubs"), Card("3", "diamonds")]
        player = player.left
        player.hole_cards = [Card("10", "diamonds"), Card("3", "hearts")]

        round.apply_player_action(p1, "bet", 900)
        round.apply_player_action(p2, "call", 900)
        round.apply_player_action(p3, "call", 900)
        round.apply_player_action(p3, "fold", None)

        for _ in range(round.table.num_seats):
            player.determine_best_hand(round.board)
            player = player.left

        round.is_action_finished = True
        round.is_poker_round_over = True
        pot_award_info = round.end_poker_round()
        self.assertEqual(pot_award_info[0]["hand_rank"], "Full House")
        self.assertEqual(pot_award_info[1]["hand_rank"], "By Default")

class TestBugs(unittest.TestCase):
    def test_allin_player_bug(self):
        game = PokerRound([Player("kenna", 400), Player("hotbrian", 980), Player("soljt", 1620)], 10, 20)

        actions = ["call", "call", "reraise 450", "call", "call"] + ["check"] * 6
        game.start_round()
        i = 0
        while i < len(actions):
            data = game.get_player_to_act_and_actions()
            player = data["player_to_act"]
            response = actions[i].split(" ")
            if len(response) < 2:
                game.handle_player_action(player, response[0], None)
            else:
                game.handle_player_action(player, response[0], int(response[1]))
            i += 1


        self.assertTrue(game.is_poker_round_over)

    def test_bb_all_in_action_not_finished_bug(self): # had to update round.allin_players after taking blinds
        p1 = Player("soljt", 1000)
        p2 = Player("kenna", 20)
        round = PokerRound([p1, p2], 10, 20)

        # start game
        round.start_round()
        player = round.table.btn
        player.hole_cards = [Card("J", "clubs"), Card("6", "diamonds")]
        player = player.left
        player.hole_cards = [Card("K", "clubs"), Card("Q", "diamonds")]
        print(round.get_player_to_act_and_actions())


        # loop here
        actions_sequence = [{"username": "soljt", "action": "call", "amount": None}, 
         {"username": "soljt", "action": "check", "amount": None},
         {"username": "soljt", "action": "check", "amount": None},
         {"username": "soljt", "action": "check", "amount": None}]
        i=0
        while not round.is_action_finished:
            action = actions_sequence[i]
            round.handle_player_action(action["username"], action["action"], action["amount"])
            if not round.is_action_finished:
                round.get_player_to_act_and_actions()
                i+=1
        # round.board = [Card("6", "hearts"), Card("K", "diamonds"), Card("Q", "hearts"), Card("6", "clubs"), Card("5", "clubs")]
        pot_award_info = round.end_poker_round()
        self.assertEqual(i, 0)

    def test_allin_player_last_to_act(self): # had to skip allin players when assigning last_to_act after a bet/raise/reraise
        p1 = Player("brian", 1000)
        p2 = Player("kenna", 10)
        p3 = Player("soljt", 500)
        round = PokerRound([p1, p2, p3], 10, 20)

        # start game
        round.start_round()
        print(round.get_player_to_act_and_actions())

        # loop here
        actions_sequence = [{"username": "brian", "action": "call", "amount": None}, 
         {"username": "soljt", "action": "reraise", "amount": 50},
         {"username": "brian", "action": "call", "amount": None}]
        i=0
        while i < len(actions_sequence):
            action = actions_sequence[i]
            round.handle_player_action(action["username"], action["action"], action["amount"])
            round.get_player_to_act_and_actions()
            if not round.is_action_finished:
                i+=1
        # round.board = [Card("6", "hearts"), Card("K", "diamonds"), Card("Q", "hearts"), Card("6", "clubs"), Card("5", "clubs")]
        self.assertEqual(round.phase, "flop")

if __name__ == "__main__":
    unittest.main()