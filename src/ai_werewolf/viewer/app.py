import json
from pathlib import Path

import streamlit as st

from ai_werewolf.persistence import load_transcript as load_transcript_file

TRANSCRIPTS_DIR = Path("transcripts")

st.set_page_config(page_title="Werewolf Replay Viewer", layout="wide")


def list_transcript_files() -> list[Path]:
    if not TRANSCRIPTS_DIR.is_dir():
        return []
    return sorted(TRANSCRIPTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def load_transcript(source) -> dict:
    if isinstance(source, Path):
        return load_transcript_file(source)
    return json.loads(source.getvalue().decode("utf-8"))


def player_label(player: dict, reveal: bool) -> str:
    status = "" if player["alive"] else " 💀"
    role = f" ({player['role'].capitalize()})" if reveal else ""
    return f"{player['name']}{role}{status}"


def render_roster(players: list[dict], reveal: bool) -> None:
    st.subheader("Players")
    cols = st.columns(len(players))
    for col, player in zip(cols, players):
        with col:
            st.markdown(f"**{player_label(player, reveal)}**")


def render_private_knowledge(players: list[dict], round_num: int) -> None:
    entries = [
        (p["name"], line)
        for p in players
        for line in p["private_log"]
        if line.startswith(f"Round {round_num}:")
    ]
    if not entries:
        return
    with st.expander("🔮 Hidden information revealed this round"):
        for name, line in entries:
            st.markdown(f"- **{name}**: {line}")


def render_round(record: dict, players: list[dict], reveal: bool) -> None:
    st.markdown("### 🌙 Night")
    st.write(record["night_result"].capitalize())

    if reveal:
        render_private_knowledge(players, record["round"])

    st.markdown("### 💬 Discussion")
    if not record["discussion"]:
        st.caption("The game ended before the day discussion.")
    else:
        for entry in record["discussion"]:
            with st.chat_message("user"):
                st.markdown(f"**{entry['name']}**: {entry['speech']}")

    st.markdown("### 🗳️ Vote")
    if record["vote_result"] is None:
        st.caption("The game ended before the day vote.")
    else:
        st.write(record["vote_result"].capitalize())


def main() -> None:
    st.title("🐺 Werewolf Replay Viewer")

    files = list_transcript_files()
    uploaded = None
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
        reveal = st.checkbox("Reveal hidden roles", value=False)

    source = uploaded if uploaded is not None else chosen_path
    if source is None:
        st.info("No transcript selected. Run `uv run python -m ai_werewolf.cli` to generate one, or upload a file.")
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

    if round_num == len(rounds) and game["winner"]:
        st.divider()
        st.success(f"🏆 {game['winner'].capitalize()} win!")


if __name__ == "__main__":
    main()
