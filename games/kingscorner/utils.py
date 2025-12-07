import os
import json
import numpy as np
from collections import OrderedDict
from .card import KingsCornerCard as Card

# Read required docs

ACTION_SPACE = OrderedDict()
ACTION_LIST = []

PILE_KEYS = ['N', 'E', 'S', 'W', 'NE', 'NW', 'SE', 'SW']

def init_deck():
    ''' Generate King's Corner deck of 52 cards
    '''
    deck = []
    card_info = Card.info
    for suit in card_info['suit']:
        for rank in card_info['rank']:
            deck.append(Card(suit, rank))
    return deck

def _build_action_space():
    deck = init_deck()
    card_strs = sorted({card.get_str() for card in deck})

    card2idx = {s: i for i, s in enumerate(card_strs)}

    action_space = OrderedDict()
    action_list = []

    for card_str in card_strs:
        for pile in PILE_KEYS:
            action_str = f"play|{card_str}|{pile}"
            action_id = len(action_list)
            action_list.append(action_str)
            action_space[action_str] = action_id

    draw_str = "draw"
    draw_id = len(action_list)
    action_list.append(draw_str)
    action_space[draw_str] = draw_id

    return card_strs, card2idx, action_space, action_list

CARD_STRS, CARD2IDX, ACTION_SPACE, ACTION_LIST = _build_action_space()
ACTION_NUM = len(ACTION_LIST)
action_num = ACTION_NUM

def cards2list(cards):
    ''' Get the corresponding string representation of cards

    Args:
        cards (list): list of KingsCornerCards objects

    Returns:
        (string): string representation of cards
    '''
    return [card.get_str() for card in cards]

def hand2dict(hand):
    ''' Get the corresponding dict representation of hand

    Args:
        hand (list): list of string of hand's card

    Returns:
        (dict): dict of hand
    '''
    hand_dict = {}
    for card in hand:
        if card not in hand_dict:
            hand_dict[card] = 1
        else:
            hand_dict[card] += 1
    return hand_dict
