import csv
from datetime import datetime, timezone
from pathlib import Path

from ai_werewolf.engine.models import GameState
from ai_werewolf.engine.roles import Role

RESULTS_PATH = Path("eval/results.csv")

FIELDNAMES = [
    "timestamp",
    "transcript_path",
    "provider",
    "model",
    "num_players",
    "num_werewolves",
    "num_seers",
    "num_doctors",
    "winner",
    "rounds_played",
    "werewolves_caught",
    "seer_present",
    "seer_investigations",
    "seer_correct_identifications",
]


def summarize_game(game: GameState, provider: str, model: str, transcript_path: str | Path) -> dict:
    """One evaluation row's worth of metrics pulled out of a finished game.

    Kept independent of the full transcript JSON: this is the compact,
    append-only record meant for cross-game reporting, not replay.
    """
    werewolves = [p for p in game.players if p.role == Role.WEREWOLF]
    seers = [p for p in game.players if p.role == Role.SEER]
    doctors = [p for p in game.players if p.role == Role.DOCTOR]

    # The only way a werewolf dies is by day vote (night kills never target a
    # werewolf), so "not alive" here means "got caught".
    werewolves_caught = sum(1 for p in werewolves if not p.alive)

    seer_investigations = sum(len(p.private_log) for p in seers)
    seer_correct_identifications = sum(
        1 for p in seers for line in p.private_log if line.endswith("ARE a Werewolf.")
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transcript_path": str(transcript_path),
        "provider": provider,
        "model": model,
        "num_players": len(game.players),
        "num_werewolves": len(werewolves),
        "num_seers": len(seers),
        "num_doctors": len(doctors),
        "winner": game.winner.value if game.winner is not None else "",
        "rounds_played": len(game.rounds),
        "werewolves_caught": werewolves_caught,
        "seer_present": bool(seers),
        "seer_investigations": seer_investigations,
        "seer_correct_identifications": seer_correct_identifications,
    }


def append_result(row: dict, path: str | Path = RESULTS_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
