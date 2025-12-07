from kingscorner import KingsCornerEnv  # adjust if in a subfolder

def main():
    # pass a config dict; Env will merge with DEFAULT_GAME_CONFIG
    env = KingsCornerEnv(config={})

    # basic reset + one step check
    out = env.reset()
    if isinstance(out, tuple):
        state = out[0]
    else:
        state = out

    print("Initial state keys:", state.keys())
    print("Legal actions:", state['legal_actions'])

    # take one random legal action
    legal_actions = list(state['legal_actions'].keys())
    action = legal_actions[0]
    step_out = env.step(action)

    if len(step_out) == 3:
        next_state, reward, done = step_out
        info = {}
    else:
        next_state, reward, done, info = step_out

    print("After 1 step: reward =", reward, "done =", done)

if __name__ == "__main__":
    main()
