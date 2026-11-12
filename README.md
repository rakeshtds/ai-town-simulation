# AI Town Simulation

A small virtual town where AI characters live their day: each resident has a name, a job, a personality, a daily schedule and a memory of past conversations — and when two residents end up in the same place at the same time, they talk.

## Features

- Agent model: name, role, personality, hour-by-hour schedule, bounded conversation memory
- Tick-based engine: one tick = one hour (06:00–22:00); agents follow schedules, meet when co-located, and hold short conversations
- Memory: after each conversation both agents store a summary, which feeds their later dialogue
- Two dialogue backends:
  - **Mock mode (default)** — deterministic template dialogue with a seeded RNG; runs anywhere with zero API keys
  - **Ollama mode** — real LLM dialogue against a local Ollama server
- Conversation caps keep a day readable (max 3 conversations per agent per day)
- Full day transcript printed and optionally saved to a file

## Architecture

`town/world.py` holds locations and co-location detection. `town/agents.py` defines residents and their schedules/memory. `town/engine.py` advances ticks, triggers conversations when agents share a location, and delegates line generation to the dialogue backend. `town/run.py` is the CLI.

## Tech Stack

Python 3.11 (stdlib only for mock mode) · Ollama (optional, local LLM)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # nothing required for mock mode
# optional: install Ollama and pull a model for LLM dialogue
ollama pull llama3.1
```

## Usage

```bash
python -m town.run --days 2                      # deterministic mock dialogue
python -m town.run --days 1 --backend ollama     # local LLM dialogue
python -m town.run --days 3 --out transcript.txt --seed 42
```

## Example Output

```
=== Day 1 ===

[08:00 @ Data Office] Dev and ... talk:
  Dev: Morning! How's the pipeline migration coming along?
  ...
[12:00 @ Cafe] Maya and Tom talk:
  Maya: Good to see you. Anything new with the morning bread batch?
```

## Project Structure

```
town/agents.py   Resident definitions, schedules, memory
town/world.py    Locations, time grid, co-location detection
town/engine.py   Simulation loop + mock / Ollama dialogue backends
town/run.py      CLI entry point
```

## Roadmap

- Persistent memory across days (SQLite) with reflection summaries
- Needs/goals system so agents choose locations instead of only following schedules
- Map visualization of the town during a run

---

An original implementation built for portfolio purposes. Sample data is synthetic.
