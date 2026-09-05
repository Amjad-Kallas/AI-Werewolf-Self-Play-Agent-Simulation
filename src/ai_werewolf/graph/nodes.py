import random
from typing import Callable

from ai_werewolf.engine.roles import Team
from ai_werewolf.engine.voting import tally_votes, tally_votes_with_tiebreak
from ai_werewolf.engine.win_conditions import check_win_condition
from ai_werewolf.llm.agent import LLMAgent

from .state import GraphState


def make_night_node(agent: LLMAgent, rng: random.Random) -> Callable[[GraphState], GraphState]:
    def night_node(state: GraphState) -> GraphState:
        game = state["game"]
        game.round += 1

        wolves = game.alive_by_team(Team.WEREWOLVES)
        votes = {wolf.id: agent.choose_night_target(game, wolf).target_id for wolf in wolves}
        target_id = tally_votes_with_tiebreak(votes, rng)

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


def resolution_node(state: GraphState) -> GraphState:
    """Round bookkeeping between a completed vote and the next night."""
    return {"game": state["game"], "discussion": []}


def route_after_night(state: GraphState) -> str:
    return "end" if state["game"].winner is not None else "discussion"


def route_after_vote(state: GraphState) -> str:
    return "end" if state["game"].winner is not None else "resolution"
