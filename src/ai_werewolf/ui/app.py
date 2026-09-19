import streamlit as st

from ai_werewolf.ui.play import render_play_tab
from ai_werewolf.ui.replay import render_replay_tab

st.set_page_config(page_title="Werewolf", layout="wide")


def main() -> None:
    st.title("🐺 Werewolf")

    play_tab, replay_tab = st.tabs(["🎮 Play", "📼 Replay"])
    with play_tab:
        render_play_tab()
    with replay_tab:
        render_replay_tab()


if __name__ == "__main__":
    main()
