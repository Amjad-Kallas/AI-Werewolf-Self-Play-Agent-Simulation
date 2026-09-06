import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "src" / "ai_werewolf" / "viewer" / "app.py")

SAMPLE_TRANSCRIPT = {
    "players": [
        {"id": 0, "name": "Alice", "role": "villager", "alive": True, "private_log": []},
        {"id": 1, "name": "Bob", "role": "werewolf", "alive": False, "private_log": []},
        {
            "id": 2,
            "name": "Carol",
            "role": "seer",
            "alive": True,
            "private_log": ["Round 1: you investigated Bob (id 1) - they ARE a Werewolf."],
        },
    ],
    "winner": "villagers",
    "rounds": [
        {
            "round": 1,
            "night_result": "no one died.",
            "discussion": [{"player_id": 0, "name": "Alice", "speech": "I suspect Bob."}],
            "vote_result": "Bob was voted out.",
        }
    ],
    "summary": "",
}


@pytest.fixture
def transcripts_cwd(tmp_path, monkeypatch):
    transcripts_dir = tmp_path / "transcripts"
    transcripts_dir.mkdir()
    (transcripts_dir / "sample.json").write_text(json.dumps(SAMPLE_TRANSCRIPT), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_app_loads_default_transcript_without_error(transcripts_cwd):
    at = AppTest.from_file(APP_PATH)
    at.run()

    assert not at.exception
    assert any("Alice" in md.value for md in at.markdown)
    assert any("Bob was voted out" in md.value for md in at.markdown)


def test_reveal_checkbox_shows_roles_and_hidden_investigation(transcripts_cwd):
    at = AppTest.from_file(APP_PATH)
    at.run()

    # nothing revealed by default
    assert not any("Werewolf" in md.value for md in at.markdown)
    assert not any("investigated Bob" in md.value for md in at.markdown)

    at.checkbox[0].set_value(True).run()

    assert not at.exception
    assert any("Werewolf" in md.value for md in at.markdown)
    assert any("investigated Bob" in md.value for md in at.markdown)


def test_shows_winner_banner_on_final_round(transcripts_cwd):
    at = AppTest.from_file(APP_PATH)
    at.run()

    assert not at.exception
    assert any("Villagers win" in s.value for s in at.success)


def test_no_transcript_available_shows_info_message(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    at = AppTest.from_file(APP_PATH)
    at.run()

    assert not at.exception
    assert any("No transcript selected" in i.value for i in at.info)
