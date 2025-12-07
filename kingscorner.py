import numpy as np
from collections import OrderedDict

from rlcard.envs import Env
from rlcard.games.kingscorner import Game
from rlcard.games.kingscorner.utils import ACTION_SPACE, ACTION_LIST, cards2list, PILE_KEYS

features = 10
features_per_pile = 4
vector_len = features + features_per_pile * len(PILE_KEYS)

DEFAULT_GAME_CONFIG = {
        'game_num_players': 2,
        }

PILE_ORDER = ['N', 'E', 'S', 'W', 'NE', 'NW', 'SE', 'SW']

RANK_VALUE = {
    'Ace': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'Jack': 11,
    'Queen': 12,
    'King': 13,
}

RED_SUITS = {'Heart', 'Diamond'}

class KingsCornerEnv(Env):

    def __init__(self, config):
        self.name = 'kingscorner'
        self.default_game_config = DEFAULT_GAME_CONFIG
        self.game = Game()
        super().__init__(config)
        self.state_shape = [[vector_len] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def _extract_state(self, state):
        hand_size = len(state['hand'])
        deck_size = state['deck_size']
        current_player = state['current_player']
        total_in_hands = sum(state['num_cards'])
        opp_hand_size = total_in_hands - hand_size

        suits = ['Heart', 'Diamond', 'Club', 'Spade']
        hand_suit_counts = {s: 0 for s in suits}
        num_kings = 0

        for card_str in state['hand']:
            suit, rank = card_str.split('-')
            if suit in hand_suit_counts:
                hand_suit_counts[suit] += 1
            if rank == 'King':
                num_kings += 1

        empty_piles = 0
        for pile_key, pile_cards in state['layout'].items():
            if len(pile_cards) == 0:
                empty_piles += 1

        rank_value_map = {
            'Ace': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            'Jack': 11,
            'Queen': 12,
            'King': 13,
        }

        pile_features = []
        corner_keys = {'NE', 'NW', 'SE', 'SW'}

        for pile_key in PILE_KEYS:
            pile_cards = state['layout'][pile_key]
            is_corner = 1.0 if pile_key in corner_keys else 0.0

            if len(pile_cards) == 0:
                pile_features.extend([1.0, is_corner, 0.0, 0.0])
            else:
                top_card_str = pile_cards[-1]
                suit, rank = top_card_str.split('-')
                rank_val = float(rank_value_map.get(rank, 0))
                is_red = 1.0 if suit in ['Heart', 'Diamond'] else 0.0
                pile_features.extend([0.0, is_corner, rank_val, is_red])

        obs_list = [
            float(hand_size),
            float(deck_size),
            float(current_player),
            float(opp_hand_size),
            float(hand_suit_counts['Heart']),
            float(hand_suit_counts['Diamond']),
            float(hand_suit_counts['Club']),
            float(hand_suit_counts['Spade']),
            float(num_kings),
            float(empty_piles),
        ] + pile_features

        obs = np.array(obs_list, dtype=np.float32)

        legal_action_id = self._get_legal_actions()
        extracted_state = {'obs': obs, 'legal_actions': legal_action_id}
        extracted_state['raw_obs'] = state
        extracted_state['raw_legal_actions'] = [a for a in state['legal_actions']]
        extracted_state['action_record'] = self.action_recorder
        return extracted_state

    def get_payoffs(self):
        return np.array(self.game.get_payoffs())

    def _get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = {ACTION_SPACE[action]: None for action in legal_actions}
        return OrderedDict(legal_ids)
    
    def _decode_action(self, action_id):
        legal_ids = self._get_legal_actions()
        if action_id in legal_ids:
            return ACTION_LIST[action_id]
        legal_id_list = list(legal_ids.keys())
        return ACTION_LIST[np.random.choice(legal_id_list)]

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        state = {}
        state['num_players'] = self.num_players
        state['hand_cards'] = [cards2list(player.hand) for player in self.game.players]
        layout = {}
        for pile_key, pile_cards in self.game.round.layout.items():
            layout[pile_key] = cards2list(pile_cards)
        state['layout'] = layout
        state['num_deck'] = self.game.dealer.num_deck()
        state['current_player'] = self.game.round.current_player
        state['legal_actions'] = self.game.round.get_legal_actions(
            self.game.players, state['current_player'])
        return state