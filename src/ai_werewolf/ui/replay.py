import json
from pathlib import Path

import streamlit as st

from ai_werewolf.persistence import TRANSCRIPTS_DIR
from ai_werewolf.persistence import load_transcript as load_transcript_file

from .rendering import render_roster, render_round, render_winner_banner


def list_transcript_files() -> list[Path]:
    if not TRANSCRIPTS_DIR.is_dir():
        return []
    return sorted(TRANSCRIPTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def load_transcript(source) -> dict:
    if isinstance(source, Path):
        return load_transcript_file(source)
    return json.loads(source.getvalue().decode("utf-8"))


def render_replay_tab() -> None:
    files = list_transcript_files()
    with st.sidebar:
        st.header("Transcript")
        chosen_path = st.selectbox(
            "Saved games",
            options=files,
            format_func=lambda p: p.name,
            index=0 if files else None,
            placeholder="No saved transcripts found",
        )
        uploaded = st.file_uploader("...or upload a transcript JSON", type="json")
        reveal = st.checkbox("Reveal hidden roles", value=False, key="replay_reveal")

    source = uploaded if uploaded is not None else chosen_path
    if source is None:
        st.info("No transcript selected. Play a game in the Play tab, or upload a transcript file.")
        return

    game = load_transcript(source)
    players = game["players"]
    rounds = game["rounds"]

    render_roster(players, reveal)
    st.divider()

    if not rounds:
        st.warning("This transcript has no recorded rounds.")
        return

    if len(rounds) == 1:
        round_num = 1
        st.caption("Round 1 of 1")
    else:
        round_num = st.slider("Round", min_value=1, max_value=len(rounds), value=1)
    render_round(rounds[round_num - 1], players, reveal)

    if round_num == len(rounds):
        st.divider()
        render_winner_banner(game)
