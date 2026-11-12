"""Tick-based simulation engine with pluggable dialogue.

Dialogue backends:
- MockDialogue: deterministic, no API key needed (default). Lines are composed
  from role/personality/memory templates with a seeded RNG.
- OllamaDialogue: local LLM via Ollama's HTTP API (optional).
"""
from __future__ import annotations

import json
import random
import urllib.request

try:
    from .agents import Agent
    from .world import FIRST_TICK, LAST_TICK, World, tick_label
except ImportError:
    from agents import Agent
    from world import FIRST_TICK, LAST_TICK, World, tick_label

MAX_CONVERSATIONS_PER_AGENT_PER_DAY = 3
EXCHANGES_PER_CONVERSATION = 3


class MockDialogue:
    """Deterministic template dialogue — runs anywhere, no keys, reproducible."""

    OPENERS = [
        "Morning! How's the {topic} coming along?",
        "Good to see you. Anything new with the {topic}?",
        "I was just thinking about the {topic}.",
    ]
    REPLIES = [
        "Slowly but surely. Yesterday taught me a lot about it.",
        "It's going well — I tried a new approach and it worked.",
        "Honestly, I could use a second pair of eyes on it.",
    ]
    TOPICS = {
        "baker": "morning bread batch", "data engineer": "pipeline migration",
        "librarian": "new arrivals shelf", "market vendor": "weekend stall",
    }

    def __init__(self, seed: int = 7):
        self.rng = random.Random(seed)

    def conversation(self, a: Agent, b: Agent, place: str) -> list[tuple[str, str]]:
        topic = self.TOPICS.get(a.role, "day")
        lines = [
            (a.name, self.rng.choice(self.OPENERS).format(topic=topic)),
            (b.name, self.rng.choice(self.REPLIES)),
            (a.name, "Let's compare notes again tomorrow."),
        ]
        return lines


class OllamaDialogue:
    """Local LLM dialogue via Ollama (http://localhost:11434)."""

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def _generate(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = urllib.request.Request(
            f"{self.base_url}/api/generate", data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read())["response"].strip()

    def conversation(self, a: Agent, b: Agent, place: str) -> list[tuple[str, str]]:
        lines: list[tuple[str, str]] = []
        history = ""
        speaker, listener = a, b
        for _ in range(EXCHANGES_PER_CONVERSATION):
            prompt = (
                f"You are {speaker.name}, a {speaker.role} in a small town. "
                f"Personality: {speaker.personality}. You are at the {place} talking "
                f"with {listener.name} ({listener.role}). You remember: {speaker.memory_text()}. "
                f"Conversation so far:\n{history}\nSay ONE short line as {speaker.name}:"
            )
            line = self._generate(prompt).split("\n")[0]
            lines.append((speaker.name, line))
            history += f"{speaker.name}: {line}\n"
            speaker, listener = listener, speaker
        return lines


class Engine:
    """Runs the town day by day; logs a readable transcript."""

    def __init__(self, agents, dialogue=None, verbose: bool = True):
        self.world = World(agents)
        self.dialogue = dialogue or MockDialogue()
        self.verbose = verbose
        self.log: list[str] = []

    def _say(self, text: str) -> None:
        self.log.append(text)
        if self.verbose:
            print(text)

    def run_day(self, day: int) -> None:
        self._say(f"\n=== Day {day} ===")
        for agent in self.world.agents:
            agent.conversations_today = 0
        for tick in range(FIRST_TICK, LAST_TICK + 1):
            self.world.move_all(tick)
            for a, b, place in self.world.co_located():
                if a.conversations_today >= MAX_CONVERSATIONS_PER_AGENT_PER_DAY:
                    continue
                if b.conversations_today >= MAX_CONVERSATIONS_PER_AGENT_PER_DAY:
                    continue
                self._hold_conversation(a, b, place, tick)
        self._say(f"--- End of day {day}: everyone heads home to sleep. ---")

    def _hold_conversation(self, a: Agent, b: Agent, place: str, tick: int) -> None:
        self._say(f"\n[{tick_label(tick)} @ {place}] {a.name} and {b.name} talk:")
        lines = self.dialogue.conversation(a, b, place)
        for speaker, line in lines:
            self._say(f"  {speaker}: {line}")
        # Both remember a one-line summary of the encounter.
        summary = f"Day chat with {b.name} at the {place}: '{lines[0][1]}'"
        a.remember(summary)
        b.remember(f"Day chat with {a.name} at the {place}: '{lines[0][1]}'")
        a.conversations_today += 1
        b.conversations_today += 1

    def run(self, days: int = 1) -> list[str]:
        for day in range(1, days + 1):
            self.run_day(day)
        return self.log
