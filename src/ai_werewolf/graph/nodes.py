import random
from typing import Callable

from ai_werewolf.engine.models import GameState
from ai_werewolf.engine.roles import Role, Team
from ai_werewolf.engine.voting import tally_votes, tally_votes_with_tiebreak
from ai_werewolf.engine.win_conditions import check_win_condition
from ai_werewolf.llm.agent import LLMAgent

from .state import GraphState


def make_night_node(agent: LLMAgent, rng: random.Random) -> Callable[[GraphState], GraphState]:
    def night_node(state: GraphState) -> GraphState:
        game = state["game"]
        game.round += 1

        doctor = next((p for p in game.alive_players() if p.role == Role.DOCTOR), None)
        protected_id = agent.choose_doctor_protect(game, doctor).target_id if doctor else None

        for seer in (p for p in game.alive_players() if p.role == Role.SEER):
            target = game.get(agent.choose_seer_target(game, seer).target_id)
            verdict = "ARE" if target.role == Role.WEREWOLF else "are NOT"
            seer.private_log.append(
                f"Round {game.round}: you investigated {target.name} (id {target.id}) - they {verdict} a Werewolf."
            )

        wolves = game.alive_by_team(Team.WEREWOLVES)
        votes = {wolf.id: agent.choose_night_target(game, wolf).target_id for wolf in wolves}
        target_id = tally_votes_with_tiebreak(votes, rng)

        if target_id == protected_id:
            game.log.append(f"Round {game.round}: the werewolves attacked, but no one died.")
        else:
            victim = game.eliminate(target_id)
            game.log.append(f"Round {game.round}: {victim.name} was killed during the night.")

        game.winner = check_win_condition(game)
        return {"game": game, "discussion": []}

    return night_node


def make_discussion_node(agent: LLMAgent) -> Callable[[GraphState], GraphState]:
    def discussion_node(state: GraphState) -> GraphState:
        game = state["game"]
        discussion: list[dict] = []

        for player in game.alive_players():
            statement = agent.make_statement(game, player, discussion)
            discussion.append({"player_id": player.id, "name": player.name, "speech": statement.speech})
            game.log.append(f"{player.name}: {statement.speech}")

        return {"game": game, "discussion": discussion}

    return discussion_node


def make_vote_node(agent: LLMAgent) -> Callable[[GraphState], GraphState]:
    def vote_node(state: GraphState) -> GraphState:
        game = state["game"]
        discussion = state["discussion"]

        votes = {player.id: agent.choose_vote(game, player, discussion).target_id for player in game.alive_players()}
        eliminated_id = tally_votes(votes)

        if eliminated_id is None:
            game.log.append(f"Round {game.round}: the vote was tied, no one was eliminated.")
        else:
            eliminated = game.eliminate(eliminated_id)
            game.log.append(f"Round {game.round}: {eliminated.name} was voted out.")

        game.winner = check_win_condition(game)
        return {"game": game, "discussion": discussion}

    return vote_node


def make_resolution_node(summarize: Callable[[GameState], str]) -> Callable[[GraphState], GraphState]:
    def resolution_node(state: GraphState) -> GraphState:
        game = state["game"]
        game.summary = summarize(game)
        game.summarized_through = len(game.log)
        return {"game": game, "discussion": []}

    return resolution_node


def route_after_night(state: GraphState) -> str:
    return "end" if state["game"].winner is not None else "discussion"


def route_after_vote(state: GraphState) -> str:
    return "end" if state["game"].winner is not None else "resolution"
