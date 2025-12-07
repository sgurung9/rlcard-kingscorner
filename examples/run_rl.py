''' An example of training a reinforcement learning agent on the environments in RLCard
'''
import os
import argparse

import torch

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import (
    get_device,
    set_seed,
    tournament,
    reorganize,
    Logger,
    plot_curve,
)

def train(args):

    # Check whether gpu is available
    device = get_device()
        
    # Seed numpy, torch, random
    set_seed(args.seed)

    # Make the environment with seed
    env = rlcard.make(
        args.env,
        config={
            'seed': args.seed,
        }
    )

    # Initialize the agent and use random agents as opponents
    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        if args.load_checkpoint_path != "":
            checkpoint = torch.load(args.load_checkpoint_path, map_location=device)
            agent = DQNAgent.from_checkpoint(checkpoint=checkpoint)
            agent.set_device(device)
        else:
            auto_save_every = args.save_every if args.save_every > 0 else float('inf')
            agent = DQNAgent(
                num_actions=env.num_actions,
                state_shape=env.state_shape[0],
                mlp_layers=[64,64],
                device=device,
                save_path=args.log_dir,
                save_every=auto_save_every,
                learning_rate=5e-4,
                epsilon_decay_steps=10000
            )

    agents = [agent]
    for _ in range(1, env.num_players):
        agents.append(RandomAgent(num_actions=env.num_actions))
    env.set_agents(agents)

    os.makedirs(args.log_dir, exist_ok=True)

    # Start training
    with Logger(args.log_dir) as logger:
        for episode in range(args.num_episodes):

            if args.algorithm == 'nfsp':
                agents[0].sample_episode_policy()

            # Generate data from the environment
            trajectories, payoffs = env.run(is_training=True)

            trajectories = reorganize(trajectories, payoffs)

            shaped_trajectories = [[] for _ in range(env.num_players)]

            for pid, traj in enumerate(trajectories):
                if pid != 0:
                    shaped_trajectories[pid] = traj
                    continue

                for (state, action, reward, next_state, done) in traj:
                    shaped_reward = float(reward)

                    try:
                        hand_before = len(state['raw_obs']['hand'])
                        hand_after = len(next_state['raw_obs']['hand']) if not done else hand_before
                        delta_hand = hand_before - hand_after
                        step_bonus = 0.1 * delta_hand
                        shaped_reward += step_bonus
                    except Exception:
                        pass

                    if done:
                        shaped_reward *= 5.0

                    shaped_trajectories[pid].append(
                        (state, action, shaped_reward, next_state, done)
                    )

            trajectories = shaped_trajectories

            # Feed transitions into agent memory, and train the agent
            # Here, we assume that DQN always plays the first position
            # and the other players play randomly (if any)
            for ts in trajectories[0]:
                agent.feed(ts)

            # checkpoints
            if args.save_every > 0 and episode > 0 and episode % args.save_every == 0:
                ckpt_path = os.path.join(
                    args.log_dir, f"checkpoint_dqn_ep_{episode}.pth"
                )
                torch.save(agent, ckpt_path)
                print(f"Saved checkpoint at episode {episode} -> {ckpt_path}")


            # Evaluate the performance. Play with random agents.
            if episode % args.evaluate_every == 0:
                logger.log_performance(
                    episode,
                    tournament(
                        env,
                        args.num_eval_games,
                    )[0]
                )

        # Get the paths
        csv_path, fig_path = logger.csv_path, logger.fig_path

    # Plot the learning curve
    plot_curve(csv_path, fig_path, args.algorithm)

    # Save model
    save_path = os.path.join(args.log_dir, 'model.pth')
    torch.save(agent, save_path)
    print('Model saved in', save_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("DQN/NFSP example in RLCard")
    parser.add_argument(
        '--env',
        type=str,
        default='kingscorner',
        choices=[
            'kingscorner',
        ],
    )
    parser.add_argument(
        '--algorithm',
        type=str,
        default='dqn',
        choices=[
            'dqn',
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
        '--num_episodes',
        type=int,
        default=200000,
    )
    parser.add_argument(
        '--num_eval_games',
        type=int,
        default=2000,
    )
    parser.add_argument(
        '--evaluate_every',
        type=int,
        default=500,
    )
    parser.add_argument(
        '--log_dir',
        type=str,
        default='experiments/kingscorner_dqn_result/',
    )
    
    parser.add_argument(
        "--load_checkpoint_path",
        type=str,
        default="",
    )
    
    parser.add_argument(
        "--save_every",
        type=int,
        default=500)

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    train(args)
