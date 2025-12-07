''' An example of evluating the trained models in RLCard
'''
import os
import argparse

import rlcard
from rlcard.agents import (
    DQNAgent,
    RandomAgent,
)
from rlcard.utils import (
    get_device,
    set_seed,
    tournament,
)

def load_model(model_path, env=None, position=None, device=None):
        
    if model_path == 'random':
        return RandomAgent(num_actions=env.num_actions)

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model path not found: {model_path}")

    import torch
    obj = torch.load(model_path, map_location=device, weights_only=False)

    if isinstance(obj, dict) and obj.get('agent_type') == 'DQNAgent':
        agent = DQNAgent.from_checkpoint(obj)
        agent.set_device(device)
        return agent

    if hasattr(obj, 'set_device'):
        obj.set_device(device)

    return obj

def evaluate(args):

    # Check whether gpu is available
    device = get_device()
        
    # Seed numpy, torch, random
    set_seed(args.seed)

    # Make the environment with seed
    env = rlcard.make(args.env, config={'seed': args.seed})

    # Load models
    agents = []
    for position, model_path in enumerate(args.models):
        agents.append(load_model(model_path, env, position, device))
    env.set_agents(agents)

    # Evaluate
    rewards = tournament(env, args.num_games)
    for position, reward in enumerate(rewards):
        print(position, args.models[position], reward)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Evaluation example in RLCard")
    parser.add_argument(
        '--env',
        type=str,
        default='kingscorner',
        choices=[
            'kingscorner',
        ],
    )
    parser.add_argument(
        '--models',
        nargs='*',
        default=[
            'experiments/kingscorner_result/checkpoint_dqn.pt',
            'random',
        ],
    )
    parser.add_argument(
        '--cuda',
        type=str,
        default='',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
    )
    parser.add_argument(
        '--num_games',
        type=int,
        default=10000,
    )

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    evaluate(args)
