import json
from dataclasses import asdict
from pathlib import Path

from ai_werewolf.engine.models import GameState

TRANSCRIPTS_DIR = Path("transcripts")


def game_to_dict(game: GameState) -> dict:
    """Plain-dict snapshot of a game, for both saving to disk and live rendering."""
    return {
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "role": p.role.value,
                "alive": p.alive,
                "private_log": p.private_log,
            }
            for p in game.players
        ],
        "winner": game.winner.value if game.winner is not None else None,
        "rounds": [asdict(record) for record in game.rounds],
        "summary": game.summary,
    }


def save_transcript(game: GameState, path: str | Path) -> None:
    """Dump a finished (or in-progress) game to JSON for the Streamlit app."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(game_to_dict(game), indent=2), encoding="utf-8")


def load_transcript(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
