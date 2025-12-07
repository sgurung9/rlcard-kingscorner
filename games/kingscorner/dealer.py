from rlcard.games.kingscorner.utils import init_deck


class KingsCornerDealer:
    ''' Initialize a King's Corner dealer class
    '''
    def __init__(self, np_random):
        self.np_random = np_random
        self.deck = init_deck()
        self.shuffle()

    def shuffle(self):
        ''' Shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self, player, num):
        ''' Deal some cards from deck to one player

        Args:
            player (object): The object with hand of cards
            num (int): The number of cards to be dealed
        '''
        for _ in range(num):
            player.hand.append(self.deck.pop())

    def initial_card_num(self, players, num_cards =7):
        '''
        Deal 7 cards to each player to prepare for the game
        '''
        for player in self.players:
            self.deal_cards(player, num_cards)

    def deal_foundations(self):
        '''
        4 cards from the deck are taken from the deck and placed in a cross (N,S,E,W)
        '''
        foundations = {}

        for pos in ['N', 'S', 'E', 'W']:
            if self.deck:
                foundations[pos] = [self.deck.pop()]
            else:
                foundations[pos] = []
        return foundations

    def deck_draw(self):
        ''' Draw card when a new game starts

        Returns:
            (object): The object of KingsCornerCard at the top of the deck
        '''
        if not self.deck:
            return None
        return self.deck.pop()
    
    def num_deck(self):
        '''Get the number of cards in deck'''
        return len(self.deck)