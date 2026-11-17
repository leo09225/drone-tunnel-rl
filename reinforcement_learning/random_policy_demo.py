"""
Random policy demo for TunnelExploreEnv.

Goal:
- run the custom environment step by step,
- print the chosen action, position, reward, explored ratio,
- display a simple text rendering of the map,
- summarize the episode at the end.
"""

from __future__ import annotations

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


def main() -> None:
    env = TunnelExploreEnv(
        grid_map=create_branching_tunnel_map(),
        max_steps=80,
        render_mode="ansi",
    )

    observation, info = env.reset(seed=42)
    total_reward = 0.0
    last_info = info

    print("===== RANDOM POLICY DEMO =====")
    initial_frame = env.render()
    if initial_frame is not None:
        print(initial_frame)
        print()

    for step_index in range(env.max_steps):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        last_info = info

        print(
            f"step={step_index} | "
            f"action={ACTION_NAMES[action]} | "
            f"position={info['position']} | "
            f"reward={reward:.2f} | "
            f"explored_ratio={info['explored_ratio']:.2%} | "
            f"terminated={terminated} | truncated={truncated}"
        )

        frame = env.render()
        if frame is not None:
            print(frame)
        print()

        if terminated or truncated:
            break

    print("===== EPISODE SUMMARY =====")
    print("steps:", last_info["steps"])
    print("explored_ratio:", f"{last_info['explored_ratio']:.2%}")
    print("total_reward:", f"{total_reward:.2f}")

    env.close()


if __name__ == "__main__":
    main()
