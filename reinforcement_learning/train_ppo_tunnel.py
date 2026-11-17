"""
Very small PPO baseline for TunnelExploreEnv.

Important:
- this is only a first smoke test,
- the goal is to verify that training can run,
- the objective is not to obtain a perfect agent yet.

Because the environment returns a Dict observation, we use SB3's
`MultiInputPolicy`.
We also define a tiny custom features extractor so SB3 treats the grid tensors
as structured numerical inputs rather than natural images.
"""

from __future__ import annotations

from pathlib import Path

import torch as th
import torch.nn as nn
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

try:
    from .tunnel_explore_env import TunnelExploreEnv, create_branching_tunnel_map
except ImportError:
    from tunnel_explore_env import TunnelExploreEnv, create_branching_tunnel_map


MODEL_DIR = Path("reinforcement_learning/models")
LOG_DIR = Path("reinforcement_learning/logs")
MODEL_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


class SimpleDictFeaturesExtractor(BaseFeaturesExtractor):
    """
    Very small features extractor for Dict observations.

    Why do we define it?
    SB3 may interpret 3D tensors as images and try to use a CNN extractor.
    Here our observations are small map tensors, so a simple flatten + MLP is
    easier to understand and perfectly fine for a first prototype.
    """

    def __init__(self, observation_space: spaces.Dict, features_dim: int = 128) -> None:
        self._global_map_shape = observation_space["global_map"].shape
        self._local_view_shape = observation_space["local_view"].shape
        self._ratio_shape = observation_space["explored_ratio"].shape

        flat_dim = (
            int(self._global_map_shape[0] * self._global_map_shape[1] * self._global_map_shape[2])
            + int(self._local_view_shape[0] * self._local_view_shape[1] * self._local_view_shape[2])
            + int(self._ratio_shape[0])
        )

        super().__init__(observation_space, features_dim)

        # A very small MLP is enough for this first training test.
        self.network = nn.Sequential(
            nn.Linear(flat_dim, 128),
            nn.ReLU(),
            nn.Linear(128, features_dim),
            nn.ReLU(),
        )

    def forward(self, observations: dict[str, th.Tensor]) -> th.Tensor:
        global_map = observations["global_map"].float().reshape(observations["global_map"].shape[0], -1)
        local_view = observations["local_view"].float().reshape(observations["local_view"].shape[0], -1)
        explored_ratio = observations["explored_ratio"].float().reshape(observations["explored_ratio"].shape[0], -1)

        concatenated = th.cat([global_map, local_view, explored_ratio], dim=1)
        return self.network(concatenated)


def make_env() -> Monitor:
    """
    Create the monitored training environment.
    """
    env = TunnelExploreEnv(
        grid_map=create_branching_tunnel_map(),
        max_steps=120,
        render_mode=None,
    )
    return Monitor(env)


def main() -> None:
    env = make_env()

    policy_kwargs = {
        "features_extractor_class": SimpleDictFeaturesExtractor,
        "features_extractor_kwargs": {"features_dim": 128},
    }

    model = PPO(
        policy="MultiInputPolicy",
        env=env,
        policy_kwargs=policy_kwargs,
        verbose=1,
        learning_rate=3e-4,
        n_steps=128,
        batch_size=64,
        gamma=0.99,
        tensorboard_log=str(LOG_DIR),
    )

    # This is intentionally small: we only want a first training smoke test.
    model.learn(total_timesteps=10_000)

    output_path = MODEL_DIR / "ppo_tunnel_explore"
    model.save(str(output_path))
    env.close()

    print(f"Model saved to: {output_path}.zip")


if __name__ == "__main__":
    main()
