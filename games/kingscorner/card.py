from termcolor import colored

class KingsCornerCard:

    info = {'suit':  ['Heart', 'Diamond', 'Club', 'Spade'],
            'rank': ['2', '3', '4', '5', '6', '7', '8', '9',
                    'Jack', 'Queen', 'King', 'Ace']
            }
    
    rank_value = {'Ace':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10,
                'Jack':11, 'Queen':12, 'King':13}

    def __init__(self, suit, rank):
        ''' Initialize the class of UnoCard

        Args:
            suit (str): The suit of card 'Heart', 'Diamond', ...
            rank (str): The rank of card 'Ace', '2', ...
        '''
        self.suit = suit
        self.rank = rank
        self.str = self.get_str()

    def get_str(self):
        ''' Get the string representation of card

        Return:
            (str): The string of card's suit and rank
        '''
        return self.suit + '-' + self.rank

    def color(self):
        ''' Get the corresponding color for the suit
            for heart/diamond: red
            for club/spade: black
        '''

        if self.suit in ['Heart', 'Diamond']:
            return 'red'
        return 'black'
    
    def value(self):
        ''' Get rank value
        '''
        return self.rank_value[self.rank]
    
    def is_king(self):
        return self.rank == 'King'

    @staticmethod
    def print_cards(cards):
        ''' Print out card in a nice form

        Args:
            card (str or list): The string form or a list of a card
        '''
        if isinstance(cards, str):
            cards = [cards]

        for i, card in enumerate(cards):
            suit, rank = card.split('-')
            if i < len(cards) - 1:
                print(', ', end='')