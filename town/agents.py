"""Town residents: identity, daily schedule, and conversation memory."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Agent:
    name: str
    role: str
    personality: str
    schedule: dict[int, str]          # tick (hour) -> location
    memory: list[str] = field(default_factory=list)   # remembered conversation facts
    conversations_today: int = 0

    def location_at(self, tick: int) -> str:
        """Location for a tick: schedule entry, else the most recent earlier entry."""
        if tick in self.schedule:
            return self.schedule[tick]
        earlier = [t for t in self.schedule if t < tick]
        return self.schedule[max(earlier)] if earlier else "Home"

    def remember(self, fact: str, limit: int = 20) -> None:
        self.memory.append(fact)
        self.memory = self.memory[-limit:]

    def memory_text(self) -> str:
        return "; ".join(self.memory) if self.memory else "(nothing yet)"


def default_residents() -> list[Agent]:
    """A starter cast. Schedules map hour -> location."""
    return [
        Agent(
            name="Maya", role="baker", personality="warm, chatty, up early",
            schedule={6: "Bakery", 7: "Bakery", 8: "Bakery", 12: "Cafe", 14: "Market", 18: "Park", 20: "Home"},
        ),
        Agent(
            name="Dev", role="data engineer", personality="dry humour, precise, curious about metrics",
            schedule={6: "Home", 8: "Data Office", 9: "Data Office", 12: "Cafe", 15: "Library", 18: "Park", 20: "Home"},
        ),
        Agent(
            name="Priya", role="librarian", personality="thoughtful, well-read, asks good questions",
            schedule={6: "Home", 9: "Library", 10: "Library", 12: "Park", 14: "Library", 17: "Cafe", 20: "Home"},
        ),
        Agent(
            name="Tom", role="market vendor", personality="boisterous, practical, knows everyone's business",
            schedule={6: "Market", 7: "Market", 12: "Cafe", 15: "Market", 18: "Home", 20: "Home"},
        ),
    ]
