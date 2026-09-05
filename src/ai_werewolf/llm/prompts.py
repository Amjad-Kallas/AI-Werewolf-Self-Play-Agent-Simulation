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


def describe_log(state: GameState, max_entries: int = 20) -> str:
    if not state.log:
        return "(no events yet)"
    return "\n".join(state.log[-max_entries:])


def describe_discussion(discussion: list[dict]) -> str:
    if not discussion:
        return "(no one has spoken yet this round)"
    return "\n".join(f"{entry['name']} (id {entry['player_id']}): {entry['speech']}" for entry in discussion)


def private_context(state: GameState, player: Player) -> str:
    if player.role != Role.WEREWOLF:
        return f"You are {player.name} (id {player.id}), a Villager. You do not know anyone's true role."

    allies = [p for p in state.alive_players() if p.role == Role.WEREWOLF and p.id != player.id]
    if allies:
        ally_desc = ", ".join(f"{p.name} (id {p.id})" for p in allies)
        pack_note = f"Your fellow werewolves (also alive) are: {ally_desc}. Never reveal this to villagers."
    else:
        pack_note = "You are the only werewolf left alive."
    return f"You are {player.name} (id {player.id}), a Werewolf. {pack_note} Blend in and avoid suspicion during the day."


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
