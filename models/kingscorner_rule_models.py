''' KingsCorner rule models
'''

import numpy as np

import rlcard
from rlcard.models.model import Model

class KingsCornerRuleAgentV1(object):
    ''' KingsCorner Rule agent version 1
    '''

    def __init__(self):
        self.use_raw = True

    def step(self, state):
        ''' Predict the action given raw state. 

        Args:
            state (dict): Raw state from the game

        Returns:
            action (str): Predicted action
        '''

        legal_actions = state['raw_legal_actions']
        state = state['raw_obs']
        if len(legal_actions) == 1 and legal_actions[0] =='draw':
            return 'draw'
        
        play_actions = [a for a in legal_actions if a.startswith('play-')]
        draw_available = 'draw' in legal_actions

        if play_actions:
            corner_plays = []
            non_corner_plays = []

            for action in play_actions:
                parts = action.split('-')
                if len(parts) != 3:
                    continue
                _, hand_idx_str, pile_key = parts
                if pile_key in ['NE', 'NW', 'SE', 'SW']:
                    corner_plays.append(action)
                else:
                    non_corner_plays.append(action)

            if corner_plays:
                return np.random.choice(corner_plays)
            
            return np.random.choice(non_corner_plays) if non_corner_plays else np.random.choice(play_actions)

        if draw_available:
            return 'draw'

        return np.random.choice(legal_actions)

    def eval_step(self, state):
        ''' Step for evaluation. The same to step
        '''
        return self.step(state), []

class KingsCornerRuleAgentV1(Model):
    ''' KingsCorner Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        env = rlcard.make('kingscorner')

        rule_agent = KingsCornerRuleAgentV1()
        self.rule_agents = [rule_agent for _ in range(env.num_players)]

    @property
    def agents(self):
        ''' Get a list of agents for each position in a the game

        Returns:
            agents (list): A list of agents

        '''
        return self.rule_agents

    @property
    def use_raw(self):
        ''' Indicate whether use raw state and action

        Returns:
            use_raw (boolean): True if using raw state and action
        '''
        return True


