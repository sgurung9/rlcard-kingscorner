from copy import deepcopy
import numpy as np

from .dealer import KingsCornerDealer as Dealer
from .player import KingsCornerPlayer as Player
from .round import KingsCornerRound as Round
from .utils import action_num


class KingsCornerGame:

    def __init__(self, allow_step_back=False, num_players=2):
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = num_players
        self.payoffs = [0 for _ in range(self.num_players)]
        self.dealer = None
        self.players = None
        self.round = None
        self.history = []

    def configure(self, game_config):
        ''' Specifiy some game specific parameters, such as number of players
        '''
        self.num_players = game_config['game_num_players']

    def init_game(self):
        ''' Initialize players and state

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current player's id
        '''
        # Initalize payoffs
        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize a dealer that can deal cards
        self.dealer = Dealer(self.np_random)

        # Initialize four players to play the game
        self.players = [Player(i, self.np_random) for i in range(self.num_players)]

        # Deal 7 cards to each player to prepare for the game
        for player in self.players:
            self.dealer.deal_cards(player, 7)

        # Initialize a Round
        self.round = Round(self.dealer, self.num_players, self.np_random)

        # Choose starting player
        self.round.current_player = self.np_random.randint(self.num_players)

        # flip and perfrom top card
        top_card = self.round.flip_top_card()
        self.round.perform_top_card(self.players, top_card)

        # Hisory for stepping back
        self.history = []

        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step(self, action):
        ''' Get the next state

        Args:
            action (str): A specific action

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        '''

        if self.allow_step_back:
            # First snapshot the current state
            his_dealer = deepcopy(self.dealer)
            his_round = deepcopy(self.round)
            his_players = deepcopy(self.players)
            self.history.append((his_dealer, his_players, his_round))

        self.round.proceed_round(self.players, action)
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        state = self.round.get_state(self.players, player_id)
        state['num_players'] = self.get_num_players()
        state['current_player'] = self.round.current_player
        return state

    def get_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''
        self.payoffs = [0.0 for _ in range(self.num_players)]
        winner = self.round.winner

        if winner is not None and len(winner) == 1 and self.num_players == 2:
            w = winner[0]
            l = 1 - w
            hand_sizes = [len(p.hand) for p in self.players]
            margin_cards = hand_sizes[l] - hand_sizes[w]
            margin_norm = margin_cards / 7.0

            base = 5.0
            alpha = 5.0

            reward_w = base + alpha * margin_norm
            reward_l = -base - alpha * margin_norm

            self.payoffs[w] = reward_w
            self.payoffs[l] = reward_l
            return self.payoffs

        if self.num_players == 2:
            hand_sizes = [len(p.hand) for p in self.players]
            if hand_sizes[0] < hand_sizes[1]:
                self.payoffs[0] = 3.0
                self.payoffs[1] = -3.0
            elif hand_sizes[1] < hand_sizes[0]:
                self.payoffs[0] = -3.0
                self.payoffs[1] = 3.0
            else:
                self.payoffs = [0.0, 0.0]
        return self.payoffs

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''

        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_num_players(self):
        ''' Return the number of players in Limit Texas Hold'em

        Returns:
            (int): The number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_num_actions():
        ''' Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 61 actions
        '''
        return action_num

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            (int): current player's id
        '''
        return self.round.current_player

    def is_over(self):
        ''' Check if the game is over

        Returns:
            (boolean): True if the game is over
        '''
        return self.round.is_over