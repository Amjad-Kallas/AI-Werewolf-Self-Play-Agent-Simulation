import argparse
import random
from datetime import datetime, timezone

from dotenv import load_dotenv

from ai_werewolf.engine.setup import new_game
from ai_werewolf.graph.build import build_graph
from ai_werewolf.llm.agent import LLMAgent
from ai_werewolf.llm.providers import DEFAULT_MODELS, make_llm
from ai_werewolf.persistence import TRANSCRIPTS_DIR, save_transcript

DEFAULT_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a self-play Werewolf game.")
    parser.add_argument("--provider", choices=sorted(DEFAULT_MODELS), default="ollama")
    parser.add_argument("--model", default=None, help="Override the default model for the chosen provider.")
    parser.add_argument("--temperature", type=float, default=0.7)
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = _parse_args()

    rng = random.Random()
    game = new_game(DEFAULT_NAMES, num_werewolves=2, num_seers=1, num_doctors=1, rng=rng)

    model_name = args.model or DEFAULT_MODELS[args.provider]
    llm = make_llm(args.provider, model_name, args.temperature)
    agent = LLMAgent(llm)
    app = build_graph(agent, rng)

    config = {
        "recursion_limit": 200,
        "run_name": "werewolf-self-play",
        "metadata": {"provider": args.provider, "model": model_name, "num_players": len(game.players)},
    }
    result = app.invoke({"game": game, "discussion": []}, config=config)
    final_game = result["game"]

    roles = ", ".join(f"{p.name}={p.role.value}" for p in final_game.players)
    print(f"Roles: {roles}\n")
    print("\n".join(final_game.log))
    print(f"\nWinner: {final_game.winner.value}")

    for player in final_game.players:
        if player.private_log:
            print(f"\n{player.name}'s private knowledge:")
            print("\n".join(player.private_log))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_path = TRANSCRIPTS_DIR / f"game-{timestamp}.json"
    save_transcript(final_game, out_path)
    print(f"\nSaved transcript to {out_path}")


if __name__ == "__main__":
    main()
