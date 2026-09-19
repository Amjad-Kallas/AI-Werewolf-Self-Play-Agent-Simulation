import random
from datetime import datetime, timezone

import streamlit as st

from ai_werewolf.engine.setup import new_game
from ai_werewolf.graph.build import build_graph
from ai_werewolf.llm.agent import LLMAgent
from ai_werewolf.llm.providers import DEFAULT_MODELS, make_llm
from ai_werewolf.persistence import TRANSCRIPTS_DIR, game_to_dict, save_transcript

from .rendering import render_game_feed

DEFAULT_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Karl", "Liam"]

PROVIDER_LABELS = {"ollama": "Ollama (local)", "mistral": "Mistral (API)"}


def render_play_tab() -> None:
    st.subheader("Configure a new game")

    # Outside the form so switching providers immediately updates the default model below.
    provider = st.radio(
        "Model provider",
        options=list(PROVIDER_LABELS),
        format_func=lambda p: PROVIDER_LABELS[p],
        horizontal=True,
    )

    with st.form("new_game_form"):
        names_text = st.text_area(
            "Player names (comma-separated)",
            value=", ".join(DEFAULT_NAMES[:6]),
            help="Add or remove names to change how many players are in the game.",
        )
        col1, col2, col3 = st.columns(3)
        num_werewolves = col1.number_input("Werewolves", min_value=1, max_value=5, value=2)
        num_seers = col2.number_input("Seers", min_value=0, max_value=1, value=1)
        num_doctors = col3.number_input("Doctors", min_value=0, max_value=1, value=1)

        model_name = st.text_input("Model", value=DEFAULT_MODELS[provider])
        temperature = st.slider("Model temperature", 0.0, 1.5, 0.7, 0.1)
        reveal_live = st.checkbox("Reveal hidden roles while playing", value=False)

        submitted = st.form_submit_button("▶️ Start Game")

    if submitted:
        _run_new_game(
            names_text=names_text,
            num_werewolves=num_werewolves,
            num_seers=num_seers,
            num_doctors=num_doctors,
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            reveal_live=reveal_live,
        )
        return

    if "last_played_game" in st.session_state:
        st.divider()
        st.caption("Most recently played game")
        reveal = st.checkbox("Reveal hidden roles", value=False, key="play_tab_reveal")
        render_game_feed(st.session_state["last_played_game"], reveal)


def _run_new_game(
    names_text: str,
    num_werewolves: int,
    num_seers: int,
    num_doctors: int,
    provider: str,
    model_name: str,
    temperature: float,
    reveal_live: bool,
) -> None:
    names = [n.strip() for n in names_text.split(",") if n.strip()]
    rng = random.Random()

    try:
        game = new_game(names, num_werewolves=num_werewolves, num_seers=num_seers, num_doctors=num_doctors, rng=rng)
    except ValueError as exc:
        st.error(f"Can't start that game: {exc}")
        return

    try:
        llm = make_llm(provider, model_name, temperature)
        agent = LLMAgent(llm)
        graph = build_graph(agent, rng)
    except Exception as exc:
        st.error(f"Couldn't set up {PROVIDER_LABELS[provider]} model '{model_name}': {exc}")
        return

    game_area = st.empty()
    final_game = None
    config = {"recursion_limit": 300, "run_name": "werewolf-self-play", "metadata": {"provider": provider, "model": model_name}}

    try:
        with st.spinner("Playing..."):
            for state in graph.stream({"game": game, "discussion": []}, config=config, stream_mode="values"):
                final_game = state["game"]
                with game_area.container():
                    render_game_feed(game_to_dict(final_game), reveal_live)
    except Exception as exc:
        st.error(f"The game stopped early: {exc}")
        return

    if final_game is None:
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = TRANSCRIPTS_DIR / f"game-{timestamp}.json"
    save_transcript(final_game, out_path)
    st.session_state["last_played_game"] = game_to_dict(final_game)
    st.toast(f"Saved transcript to {out_path}")
