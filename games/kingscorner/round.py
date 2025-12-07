from rlcard.games.kingscorner.utils import cards2list, PILE_KEYS

pile_dir = ['N', 'E', 'S', 'W', 'NE', 'NW', 'SE', 'SW']

class KingsCornerRules:
    def can_start_pile(card, is_corner_spot: bool) -> bool:
        if is_corner_spot:
            return getattr(card, "rank", None) == "King"
        return True

    def can_stack_on(card, dest_card) -> bool:
        return True
    
class KingsCornerRound:

    def __init__(self, dealer, num_players, np_random):
        ''' Initialize the round class

        Args:
            dealer (object): the object of KingsCornerDealer
            num_players (int): the number of players in game
        '''
        self.np_random = np_random
        self.dealer = dealer
        self.num_players = num_players
        self.direction = 0
        self.is_over = False
        self.winner = None

        foundations = self.dealer.deal_foundations()
        self.layout = {
            'N': foundations.get('N', []),
            'E': foundations.get('E', []),
            'S': foundations.get('S', []),
            'W': foundations.get('W', []),
            'NE': [],
            'NW': [],
            'SE': [],
            'SW': [],
        }

        self.current_player = 0
        self.played_cards = []

    def flip_top_card(self):
        return self.dealer.deck_draw()

    def perform_top_card(self, players, top_card):
        if top_card is None:
            return
        self.played_cards.append(top_card)

    def proceed_round(self, players, action):
        ''' Call other Classes' functions to keep round running

        Args:
            player (object): object of KingsCornerPlayer
            action (str): string of legal action
        '''
        if self.is_over:
            return
        
        if action == 'draw':
            self._perform_draw_action(players)
            return None
        
        parts = action.split('|')
        if len(parts) != 3 or parts[0] != 'play':
            raise ValueError(f"Invalid action format: {action}")

        _, card_str, pile_key = parts

        if pile_key not in self.layout:
            raise ValueError(f"Invalid pile key: {pile_key}")

        player = players[self.current_player]
        hand_strs = cards2list(player.hand)

        try:
            hand_idx = hand_strs.index(card_str)
        except ValueError:
            raise ValueError(f"Card {card_str} not found in player hand")

        card = player.hand[hand_idx]
        pile = self.layout[pile_key]

        dest_is_corner = pile_key in ['NE', 'NW', 'SE', 'SW']
        dest_is_empty = len(pile) == 0

        if dest_is_empty:
            if not KingsCornerRules.can_start_pile(card, is_corner_spot=dest_is_corner):
                raise ValueError(f"Illegal move: cannot start pile {pile_key} with {card}")
        else:
            top_dest = pile[-1]
            if not KingsCornerRules.can_stack_on(card, top_dest):
                raise ValueError(f"Illegal move: cannot place {card} on {top_dest} in pile {pile_key}")

        player.hand.pop(hand_idx)
        pile.append(card)

        if not player.hand:
            self.is_over = True
            self.winner = [self.current_player]
            return

        self.current_player = (self.current_player + 1) % self.num_players

    def get_legal_actions(self, players, player_id):
        legal_actions = []
        player = players[player_id]
        hand = player.hand
        hand_strs = cards2list(hand)

        for idx, card in enumerate(hand):
            card_str = hand_strs[idx]
            for pile_key in pile_dir:
                pile = self.layout[pile_key]
                dest_is_corner = pile_key in ['NE', 'NW', 'SE', 'SW']
                dest_is_empty = len(pile) == 0

                if dest_is_empty: ## rephrase
                    if KingsCornerRules.can_start_pile(card, is_corner_spot=dest_is_corner):
                        legal_actions.append(f"play|{card_str}|{pile_key}")
                else:
                    top_dest = pile[-1]
                    if KingsCornerRules.can_stack_on(card, top_dest):
                                legal_actions.append(f"play|{card_str}|{pile_key}")
        
        if not legal_actions and self.dealer.num_deck() > 0:
            legal_actions = ['draw']

        return legal_actions

    def get_state(self, players, player_id):
        ''' Get player's state

        Args:
            hand (list): cards in player's hand
            layout (dict): pile
            deck_size (int): remaining cards in deck
            legal_actions (list): legal action 
            num_cards (int): cards of each player
            current_player (int): current player
        '''
        state = {}
        player = players[player_id]
        state['hand'] = cards2list(player.hand)
        layout = {}
        for key in pile_dir:
            layout[key] = cards2list(self.layout[key])
        state['layout'] = layout

        state['deck_size'] = self.dealer.num_deck()
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        state['num_cards'] = [len(p.hand) for p in players]
        state['current_player'] = self.current_player
        return state

    def _perform_draw_action(self, players):
        card = self.dealer.deck_draw()
        if card is None:
            self.current_player = (self.current_player + 1) % self.num_players
            return

        players[self.current_player].hand.append(card)
        self.current_player = (self.current_player + 1) % self.num_players
