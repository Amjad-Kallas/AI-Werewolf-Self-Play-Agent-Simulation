"""Rendering helpers shared by the replay and live-play tabs.

Both tabs work from the same plain-dict game shape produced by
`ai_werewolf.persistence.game_to_dict` (and its JSON round-trip), so a
finished live game can be displayed with exactly the same code as a
transcript loaded from disk.
"""

import streamlit as st


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


def render_winner_banner(data: dict) -> None:
    if data["winner"]:
        st.success(f"🏆 {data['winner'].capitalize()} win!")


def render_game_feed(data: dict, reveal: bool) -> None:
    """All rounds so far, one after another - used for watching a game live."""
    render_roster(data["players"], reveal)
    st.divider()
    for record in data["rounds"]:
        st.markdown(f"## Round {record['round']}")
        render_round(record, data["players"], reveal)
        st.divider()
    render_winner_banner(data)
