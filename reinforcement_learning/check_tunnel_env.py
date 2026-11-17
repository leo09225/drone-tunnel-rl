"""
Validation script for TunnelExploreEnv.

Goal:
- make sure the custom environment can be instantiated,
- optionally validate its Gymnasium API with Stable-Baselines3's check_env,
- run a short manual random rollout to ensure it does not crash.
"""

from __future__ import annotations

try:
    from stable_baselines3.common.env_checker import check_env
except ImportError:
    check_env = None

try:
    from .tunnel_explore_env import (
        ACTION_NAMES,
        TunnelExploreEnv,
        create_branching_tunnel_map,
    )
except ImportError:
    from tunnel_explore_env import (
        ACTION_NAMES,
        TunnelExploreEnv,
        create_branching_tunnel_map,
    )


def run_manual_random_test() -> None:
    """
    Run a random policy for up to 100 steps.

    This is useful even if check_env is available because it lets us inspect
    rewards and the explored ratio on a real rollout.
    """
    env = TunnelExploreEnv(
        grid_map=create_branching_tunnel_map(),
        max_steps=100,
        render_mode=None,
    )
    observation, info = env.reset(seed=42)

    print("===== MANUAL RANDOM TEST =====")

    for step_index in range(100):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)

        print(
            f"step={step_index} | "
            f"action={ACTION_NAMES[action]} | "
            f"reward={reward:.2f} | "
            f"explored_ratio={info['explored_ratio']:.2%} | "
            f"terminated={terminated} | truncated={truncated}"
        )

        if terminated or truncated:
            break

    print()
    print("Final explored ratio:", f"{info['explored_ratio']:.2%}")
    print("Environment did not crash during the random rollout.")
    env.close()


def main() -> None:
    if check_env is not None:
        print("===== STABLE-BASELINES3 check_env =====")
        env = TunnelExploreEnv(grid_map=create_branching_tunnel_map(), max_steps=100)
        check_env(env, warn=True)
        env.close()
        print("check_env passed.\n")
    else:
        print("Stable-Baselines3 not installed: skipping check_env.\n")

    run_manual_random_test()


if __name__ == "__main__":
    main()
