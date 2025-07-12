// Hand examples data — using "Rank of suit" format
export const pokerHands = [
  {
    title: "Royal Flush",
    description: "The highest 5 cards, all of the same suit: A, K, Q, J, 10",
    cards: [
      "A of spades",
      "K of spades",
      "Q of spades",
      "J of spades",
      "10 of spades",
    ],
  },
  {
    title: "Straight Flush",
    description: "Any 5 consecutive cards of the same suit.",
    cards: [
      "9 of hearts",
      "8 of hearts",
      "7 of hearts",
      "6 of hearts",
      "5 of hearts",
    ],
  },
  {
    title: "Four of a Kind",
    description: '4 cards of the same rank. Also called "quads".',
    cards: [
      "9 of diamonds",
      "9 of hearts",
      "9 of spades",
      "9 of clubs",
      "2 of diamonds",
    ],
  },
  {
    title: "Full House",
    description: "3 of a kind and a pair. Also called a \"boat\".",
    cards: [
      "K of hearts",
      "K of clubs",
      "K of spades",
      "5 of diamonds",
      "5 of spades",
    ],
  },
  {
    title: "Flush",
    description: "Any 5 cards of the same suit.",
    cards: [
      "2 of clubs",
      "5 of clubs",
      "9 of clubs",
      "J of clubs",
      "Q of clubs",
    ],
  },
  {
    title: "Straight",
    description: "5 consecutive cards of mixed suits. Referred to as \"broadway\" when made with the highest 5 cards.",
    cards: [
      "6 of diamonds",
      "7 of hearts",
      "8 of spades",
      "9 of clubs",
      "10 of hearts",
    ],
  },
  {
    title: "Three of a Kind",
    description: "3 cards of the same rank. Also called \"trips\" or a \"set\".",
    cards: [
      "7 of clubs",
      "7 of diamonds",
      "7 of hearts",
      "2 of spades",
      "9 of hearts",
    ],
  },
  {
    title: "Two Pair",
    description: "2 different pairs.",
    cards: [
      "4 of spades",
      "4 of clubs",
      "9 of diamonds",
      "9 of spades",
      "J of hearts",
    ],
  },
  {
    title: "One Pair",
    description: "2 cards of the same rank.",
    cards: [
      "8 of hearts",
      "8 of spades",
      "5 of clubs",
      "2 of diamonds",
      "10 of diamonds",
    ],
  },
  {
    title: "High Card",
    description: "When no other hand is made, you're stuck with high card.",
    cards: [
      "2 of hearts",
      "5 of diamonds",
      "9 of clubs",
      "J of spades",
      "A of clubs",
    ],
  },
];