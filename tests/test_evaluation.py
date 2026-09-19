import csv

from ai_werewolf.engine.models import GameState, Player, RoundRecord
from ai_werewolf.engine.roles import Role, Team
from ai_werewolf.evaluation import FIELDNAMES, append_result, summarize_game


def make_game() -> GameState:
    players = [
        Player(id=0, name="Alice", role=Role.VILLAGER, alive=True),
        Player(id=1, name="Bob", role=Role.WEREWOLF, alive=False),
        Player(id=2, name="Carol", role=Role.WEREWOLF, alive=True),
        Player(
            id=3,
            name="Dave",
            role=Role.SEER,
            alive=True,
            private_log=[
                "Round 1: you investigated Bob (id 1) - they ARE a Werewolf.",
                "Round 2: you investigated Alice (id 0) - they are NOT a Werewolf.",
            ],
        ),
        Player(id=4, name="Eve", role=Role.DOCTOR, alive=True),
    ]
    game = GameState(players=players, winner=Team.WEREWOLVES)
    game.rounds = [RoundRecord(round=1, night_result="x"), RoundRecord(round=2, night_result="y")]
    return game


def test_summarize_game_counts_roles_and_outcomes():
    game = make_game()
    row = summarize_game(game, provider="ollama", model="qwen2.5:3b", transcript_path="transcripts/x.json")

    assert row["provider"] == "ollama"
    assert row["model"] == "qwen2.5:3b"
    assert row["num_players"] == 5
    assert row["num_werewolves"] == 2
    assert row["num_seers"] == 1
    assert row["num_doctors"] == 1
    assert row["winner"] == "werewolves"
    assert row["rounds_played"] == 2
    assert row["werewolves_caught"] == 1  # Bob is dead, Carol survived
    assert row["seer_present"] is True
    assert row["seer_investigations"] == 2
    assert row["seer_correct_identifications"] == 1  # only the Bob investigation was a real werewolf


def test_summarize_game_with_no_seer():
    game = make_game()
    for p in game.players:
        if p.role == Role.SEER:
            p.role = Role.VILLAGER

    row = summarize_game(game, provider="ollama", model="qwen2.5:3b", transcript_path="x.json")

    assert row["num_seers"] == 0
    assert row["seer_present"] is False
    assert row["seer_investigations"] == 0
    assert row["seer_correct_identifications"] == 0


def test_append_result_writes_header_once_and_appends_rows(tmp_path):
    path = tmp_path / "nested" / "results.csv"
    game = make_game()
    row1 = summarize_game(game, provider="ollama", model="qwen2.5:3b", transcript_path="a.json")
    row2 = summarize_game(game, provider="mistral", model="mistral-small-latest", transcript_path="b.json")

    append_result(row1, path)
    append_result(row2, path)

    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert rows[0]["provider"] == "ollama"
    assert rows[1]["provider"] == "mistral"
    assert list(rows[0].keys()) == FIELDNAMES
