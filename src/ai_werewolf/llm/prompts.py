from ai_werewolf.engine.models import GameState, Player
from ai_werewolf.engine.roles import Role

BASE_RULES = (
    "You are playing Werewolf (a.k.a. Mafia), a social deduction game. "
    "Werewolves secretly eliminate one villager each night. During the day, everyone "
    "discusses and then votes to eliminate a suspect. Villagers win when all werewolves "
    "are dead; werewolves win once they equal or outnumber the villagers."
)


def describe_players(state: GameState) -> str:
    return "\n".join(f"- id {p.id}: {p.name}" for p in state.alive_players())


def describe_log(state: GameState) -> str:
    """Rolling summary of earlier rounds plus the raw events since it was last updated.

    Keeps prompt size bounded across a long game instead of replaying the
    full transcript every call.
    """
    fresh = state.log[state.summarized_through :]
    parts = []
    if state.summary:
        parts.append(f"Summary of earlier rounds:\n{state.summary}")
    parts.append("Recent events:\n" + ("\n".join(fresh) if fresh else "(none yet)"))
    return "\n\n".join(parts)


def describe_discussion(discussion: list[dict]) -> str:
    if not discussion:
        return "(no one has spoken yet this round)"
    return "\n".join(f"{entry['name']} (id {entry['player_id']}): {entry['speech']}" for entry in discussion)


def private_context(state: GameState, player: Player) -> str:
    if player.role == Role.WEREWOLF:
        allies = [p for p in state.alive_players() if p.role == Role.WEREWOLF and p.id != player.id]
        if allies:
            ally_desc = ", ".join(f"{p.name} (id {p.id})" for p in allies)
            pack_note = f"Your fellow werewolves (also alive) are: {ally_desc}. Never reveal this to villagers."
        else:
            pack_note = "You are the only werewolf left alive."
        return f"You are {player.name} (id {player.id}), a Werewolf. {pack_note} Blend in and avoid suspicion during the day."

    if player.role == Role.SEER:
        history = "\n".join(player.private_log) if player.private_log else "(you haven't investigated anyone yet)"
        return (
            f"You are {player.name} (id {player.id}), a Seer. Each night you may investigate one living "
            "player to learn whether they are a Werewolf. Never reveal your role to anyone.\n"
            f"Your investigation history:\n{history}"
        )

    if player.role == Role.DOCTOR:
        return (
            f"You are {player.name} (id {player.id}), a Doctor. Each night you may choose one living player "
            "(including yourself) to protect from a werewolf attack. Never reveal your role to anyone."
        )

    return f"You are {player.name} (id {player.id}), a Villager. You do not know anyone's true role."


def night_prompt(state: GameState, wolf: Player) -> tuple[str, str]:
    system = f"{BASE_RULES}\n\n{private_context(state, wolf)}"
    targets = "\n".join(f"- id {p.id}: {p.name}" for p in state.alive_players() if p.role != Role.WEREWOLF)
    human = (
        f"It is night, round {state.round}.\n\n"
        f"Game log so far:\n{describe_log(state)}\n\n"
        f"Players you may eliminate:\n{targets}\n\n"
        "Choose one to eliminate tonight."
    )
    return system, human


def seer_prompt(state: GameState, seer: Player) -> tuple[str, str]:
    system = f"{BASE_RULES}\n\n{private_context(state, seer)}"
    targets = "\n".join(f"- id {p.id}: {p.name}" for p in state.alive_players() if p.id != seer.id)
    human = (
        f"It is night, round {state.round}.\n\n"
        f"Game log so far:\n{describe_log(state)}\n\n"
        f"Players you may investigate:\n{targets}\n\n"
        "Choose one to investigate tonight."
    )
    return system, human


def doctor_prompt(state: GameState, doctor: Player) -> tuple[str, str]:
    system = f"{BASE_RULES}\n\n{private_context(state, doctor)}"
    targets = "\n".join(f"- id {p.id}: {p.name}" for p in state.alive_players())
    human = (
        f"It is night, round {state.round}.\n\n"
        f"Game log so far:\n{describe_log(state)}\n\n"
        f"Players you may protect:\n{targets}\n\n"
        "Choose one to protect tonight."
    )
    return system, human


def discussion_prompt(state: GameState, player: Player, discussion: list[dict]) -> tuple[str, str]:
    system = f"{BASE_RULES}\n\n{private_context(state, player)}"
    human = (
        f"It is the day discussion, round {state.round}.\n\n"
        f"Alive players:\n{describe_players(state)}\n\n"
        f"Game log so far:\n{describe_log(state)}\n\n"
        f"Discussion so far this round:\n{describe_discussion(discussion)}\n\n"
        "Say something to the group: share a suspicion, defend yourself, or ask a question. "
        "Keep it to 1-3 sentences."
    )
    return system, human


def vote_prompt(state: GameState, player: Player, discussion: list[dict]) -> tuple[str, str]:
    system = f"{BASE_RULES}\n\n{private_context(state, player)}"
    targets = "\n".join(f"- id {p.id}: {p.name}" for p in state.alive_players() if p.id != player.id)
    human = (
        f"It is the day vote, round {state.round}.\n\n"
        f"Players you may vote for:\n{targets}\n\n"
        f"Game log so far:\n{describe_log(state)}\n\n"
        f"Discussion this round:\n{describe_discussion(discussion)}\n\n"
        "Cast your vote for who should be eliminated."
    )
    return system, human
