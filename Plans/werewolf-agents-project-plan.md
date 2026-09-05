# AI Werewolf: Self-Play Agent Simulation — Project Plan

## Goal

Build a multi-agent system where LLM-driven agents play Werewolf (social deduction) against each other. Showcase agent orchestration, hidden-state management, structured decision-making, and evaluation — with a local-first, low-cost development workflow.

## Tech stack

- **Python 3.10+**
- **LangGraph** — state machine for game phases (Night / Day / Vote), shared + private state
- **Ollama + Qwen2.5-3B (quantized)** — local model for development/debugging, free and unlimited
- **Claude Haiku 4.5 (API)** — swapped in later for showcase-quality games
- **Pydantic** — structured output schemas (speech, vote, reasoning) for every agent decision
- **SQLite** — game/round persistence once you move past in-memory state
- **LangSmith** (free tier) — tracing/observability, wired in from day one
- **Streamlit** — replay viewer (simplest path to a shareable demo)
- **pytest** — tests for game engine logic (win conditions, vote tallying, role assignment)
- **Git** — version control with clear, incremental commits

## Architecture overview

- **Game engine (plain code, not LLM)**: enforces rules, tracks alive/dead state, tallies votes, checks win conditions. Never trust an LLM to self-referee.
- **Moderator/Narrator**: controls what each agent is allowed to see; reveals results (e.g., who died overnight) without leaking hidden roles.
- **Agents**: each with a role (Werewolf, Villager, Seer, Doctor), a private state (what they know), and a persistent memory summary of past rounds.
- **LangGraph state graph**: nodes = `Night`, `Discussion`, `Vote`, `Resolution`; shared state = public log, alive list, round number; private state = per-agent role/knowledge/memory.
- **Structured output**: every agent call returns JSON (`{"speech": ..., "vote": ..., "reasoning": ...}`) validated via Pydantic — no scraping free text for game-critical decisions.

## Milestones

### Phase 0 — Setup
- Install Ollama, pull Qwen2.5-3B (4-bit quantized)
- Set up repo structure, `requirements.txt`/`pyproject.toml`, Git init
- Wire up LangSmith tracing (env vars only, no code changes needed)

### Phase 1 — Game engine only (no LLM)
- Implement roles, state, win conditions, vote tallying in plain Python
- Hardcode agent decisions (random or scripted) to validate the full game loop end-to-end
- Write pytest coverage for win conditions and edge cases (ties, early elimination, etc.)

### Phase 2 — LangGraph + local LLM
- Replace scripted decisions with Qwen2.5-3B calls via Ollama
- Enforce structured JSON output; add retry/repair logic for malformed responses
- Confirm a full game runs coherently start to finish

### Phase 3 — Roles with hidden information
- Add Seer (nightly investigation) and Doctor (nightly protection)
- Ensure private state per agent is correctly isolated (no leakage between agents)
- Test bluffing/deduction dynamics qualitatively — read transcripts, sanity-check reasoning

### Phase 4 — Memory across rounds
- Give agents a rolling summary of past rounds (not full transcripts, to control token cost)
- Observe whether agents reference past accusations/betrayals coherently

### Phase 5 — Switch to Claude Haiku for showcase runs
- Swap local model for Haiku via API for higher-quality dialogue
- Use prompt caching for repeated system prompts/role instructions to control cost
- Run a batch of "hero" games to use in the portfolio demo

### Phase 6 — Replay viewer
- Build a Streamlit app that steps through a saved game transcript round by round
- Show public discussion, eliminations, and (optionally) a reveal toggle for hidden roles

### Phase 7 — Evaluation
- Run enough games (aim ~50-100) to compute: win rate by role, how often Werewolves get caught, how often Seer info gets acted on
- Compare local Qwen2.5-3B vs. Haiku on dialogue quality/deception ability — good standalone mini-result for the writeup
- Log full reasoning traces so you can highlight specific "the agent noticed a lie" moments

### Phase 8 — Polish & portfolio packaging
- README with game explanation, architecture diagram, sample transcript excerpt, and eval charts
- Short blog post or write-up (this often gets read more than the code itself)
- Record a short demo video/gif of the replay viewer in action

## Cost notes

- Local development (Phases 0-4): free, using Qwen2.5-3B via Ollama
- API phase (Phase 5+): roughly $0.15-0.20 per game with Claude Haiku 4.5; full evaluation batch (~100 games) likely $15-20 total
- LangSmith: free tier (5,000 traces/month) comfortably covers solo development at this scale

## Stretch goals (optional, only after core project is solid)

- Add more roles (Hunter, Witch, etc.)
- Run tournaments across multiple models and compare deception/detection skill
- Extend toward a D&D-style game-master agent, reusing the LangGraph scaffolding (moderator pattern, hidden state, structured tool-driven outcomes)
