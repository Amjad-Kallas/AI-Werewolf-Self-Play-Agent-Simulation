import random

from ai_werewolf.engine.models import RoundRecord
from ai_werewolf.engine.roles import Team
from ai_werewolf.engine.setup import new_game
from ai_werewolf.persistence import load_transcript, save_transcript


def test_round_trip_preserves_players_rounds_and_winner(tmp_path):
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    game.winner = Team.VILLAGERS
    game.rounds = [
        RoundRecord(
            round=1,
            night_result="b was killed during the night.",
            discussion=[{"player_id": 0, "name": "a", "speech": "hello"}],
            vote_result="c was voted out.",
        )
    ]
    game.get(1).alive = False

    out_path = tmp_path / "game.json"
    save_transcript(game, out_path)
    data = load_transcript(out_path)

    assert data["winner"] == "villagers"
    assert len(data["players"]) == 3
    assert data["players"][1]["alive"] is False
    assert data["rounds"][0]["night_result"] == "b was killed during the night."
    assert data["rounds"][0]["discussion"][0]["speech"] == "hello"
    assert data["rounds"][0]["vote_result"] == "c was voted out."


def test_creates_parent_directories(tmp_path):
    game = new_game(["a", "b", "c"], num_werewolves=1, rng=random.Random(0))
    out_path = tmp_path / "nested" / "dir" / "game.json"

    save_transcript(game, out_path)

    assert out_path.exists()
