"""Run the AI town simulation.

Usage:
    python -m town.run [--days 2] [--backend mock|ollama] [--out transcript.txt]
Mock mode (default) needs no API key and is fully deterministic.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from town.agents import default_residents  # noqa: E402
from town.engine import Engine, MockDialogue, OllamaDialogue  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="AI town simulation")
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--backend", choices=["mock", "ollama"], default="mock")
    parser.add_argument("--model", default="llama3.1", help="Ollama model when backend=ollama")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", default=None, help="Also write the transcript to this file")
    args = parser.parse_args()

    dialogue = OllamaDialogue(model=args.model) if args.backend == "ollama" else MockDialogue(seed=args.seed)
    engine = Engine(default_residents(), dialogue=dialogue)
    log = engine.run(days=args.days)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(log) + "\n")
        print(f"\nTranscript written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
