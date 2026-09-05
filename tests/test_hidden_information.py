from ai_werewolf.engine.models import GameState, Player
from ai_werewolf.engine.roles import Role
from ai_werewolf.llm.prompts import discussion_prompt, private_context, vote_prompt


def make_state() -> GameState:
    players = [
        Player(id=0, name="Wendy", role=Role.WEREWOLF),
        Player(id=1, name="Sally", role=Role.SEER),
        Player(id=2, name="Dan", role=Role.DOCTOR),
        Player(id=3, name="Vic", role=Role.VILLAGER),
    ]
    return GameState(players=players)


def test_seer_private_investigation_is_never_shown_to_other_players():
    state = make_state()
    seer = state.get(1)
    seer.private_log.append("Round 1: you investigated Wendy (id 0) - they ARE a Werewolf.")

    # the seer's own prompts include it
    assert "you investigated Wendy" in private_context(state, seer)

    # no other player's prompt leaks it
    for other_id in (0, 2, 3):
        other = state.get(other_id)
        system, human = discussion_prompt(state, other, [])
        assert "investigated Wendy" not in system
        assert "investigated Wendy" not in human
        system, human = vote_prompt(state, other, [])
        assert "investigated Wendy" not in system
        assert "investigated Wendy" not in human

    # and it never leaks into the public game log either
    assert not any("investigated Wendy" in entry for entry in state.log)


def test_werewolf_identity_is_never_shown_to_villager_team():
    state = make_state()

    for villager_team_id in (1, 2, 3):
        player = state.get(villager_team_id)
        context = private_context(state, player)
        assert "Wendy" not in context
        assert player.role != Role.WEREWOLF


def test_doctor_and_villager_have_no_role_specific_leakage():
    state = make_state()
    doctor_context = private_context(state, state.get(2))
    villager_context = private_context(state, state.get(3))

    assert "Doctor" in doctor_context
    assert "protect" in doctor_context
    assert "Villager" in villager_context
    assert "protect" not in villager_context
