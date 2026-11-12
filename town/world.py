"""The town: locations and the daily time grid."""
from __future__ import annotations

LOCATIONS = ["Bakery", "Library", "Data Office", "Park", "Cafe", "Home", "Market"]

# Time grid: one tick = one hour, 06:00 -> 22:00, then everyone sleeps.
FIRST_TICK = 6
LAST_TICK = 22


def tick_label(tick: int) -> str:
    return f"{tick:02d}:00"


class World:
    """Where everyone is, and when two people can talk (same place, same tick)."""

    def __init__(self, agents):
        self.agents = agents
        self.positions: dict[str, str] = {a.name: "Home" for a in agents}

    def move_all(self, tick: int) -> None:
        for agent in self.agents:
            self.positions[agent.name] = agent.location_at(tick)

    def co_located(self) -> list[tuple]:
        """Pairs of agents currently in the same location (sorted, deduped)."""
        by_place: dict[str, list] = {}
        for agent in self.agents:
            by_place.setdefault(self.positions[agent.name], []).append(agent)
        pairs = []
        for place, group in by_place.items():
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    pairs.append((group[i], group[j], place))
        return pairs
