import argparse
import random
from datetime import datetime, timezone

from dotenv import load_dotenv

from ai_werewolf.engine.setup import new_game
from ai_werewolf.evaluation import RESULTS_PATH, append_result, summarize_game
from ai_werewolf.graph.build import build_graph
from ai_werewolf.llm.agent import LLMAgent
from ai_werewolf.llm.providers import DEFAULT_MODELS, make_llm
from ai_werewolf.persistence import TRANSCRIPTS_DIR, save_transcript

DEFAULT_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Karl", "Liam"]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a batch of self-play games for evaluation.")
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--provider", choices=sorted(DEFAULT_MODELS), default="ollama")
    parser.add_argument("--model", default=None, help="Override the default model for the chosen provider.")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--players", type=int, default=6)
    parser.add_argument("--werewolves", type=int, default=2)
    parser.add_argument("--seers", type=int, default=1)
    parser.add_argument("--doctors", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = _parse_args()
    model_name = args.model or DEFAULT_MODELS[args.provider]
    names = DEFAULT_NAMES[: args.players]

    for i in range(1, args.games + 1):
        rng = random.Random()
        game = new_game(names, num_werewolves=args.werewolves, num_seers=args.seers, num_doctors=args.doctors, rng=rng)

        llm = make_llm(args.provider, model_name, args.temperature)
        agent = LLMAgent(llm)
        graph = build_graph(agent, rng)
        config = {
            "recursion_limit": 300,
            "run_name": "werewolf-eval",
            "metadata": {"provider": args.provider, "model": model_name, "batch_index": i},
        }
        result = graph.invoke({"game": game, "discussion": []}, config=config)
        final_game = result["game"]

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        transcript_path = TRANSCRIPTS_DIR / f"eval-{timestamp}.json"
        save_transcript(final_game, transcript_path)

        row = summarize_game(final_game, provider=args.provider, model=model_name, transcript_path=transcript_path)
        append_result(row, RESULTS_PATH)

        print(f"[{i}/{args.games}] winner={row['winner']} rounds={row['rounds_played']} -> {transcript_path}")

    print(f"\nAppended {args.games} result(s) to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
