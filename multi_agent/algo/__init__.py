try:
    from multi_agent.algo.balancedchoice import BalancedChoiceDrone
    from multi_agent.algo.balancedchoice50 import BalancedChoiceDrone50
    from multi_agent.algo.random import RandomDrone
    from multi_agent.algo.straight import StraightDrone
    from multi_agent.algo.tremaux import TremauxDrone
    from multi_agent.algo.Unexplored import Unexplored
except ModuleNotFoundError as exc:
    if exc.name != "multi_agent":
        raise

    from algo.balancedchoice import BalancedChoiceDrone
    from algo.balancedchoice50 import BalancedChoiceDrone50
    from algo.random import RandomDrone
    from algo.straight import StraightDrone
    from algo.tremaux import TremauxDrone
    from algo.Unexplored import Unexplored

ALGO_SPECS = (
    ("n_random", RandomDrone),
    ("n_unexplored", Unexplored),
    ("n_straight", StraightDrone),
    ("n_tremaux", TremauxDrone),
    ("n_balanced_choice", BalancedChoiceDrone),
    ("n_balanced_choice_50", BalancedChoiceDrone50),
)

EXPLORATION_DRONES = tuple(drone_class for _, drone_class in ALGO_SPECS)

__all__ = [
    "ALGO_SPECS",
    "BalancedChoiceDrone",
    "BalancedChoiceDrone50",
    "EXPLORATION_DRONES",
    "RandomDrone",
    "StraightDrone",
    "Unexplored",
    "TremauxDrone",
]
