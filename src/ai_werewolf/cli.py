import random

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from ai_werewolf.engine.setup import new_game
from ai_werewolf.graph.build import build_graph
from ai_werewolf.llm.agent import LLMAgent

DEFAULT_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]


def main() -> None:
    load_dotenv()

    rng = random.Random()
    game = new_game(DEFAULT_NAMES, num_werewolves=2, num_seers=1, num_doctors=1, rng=rng)

    model_name = "qwen2.5:3b"
    llm = ChatOllama(model=model_name, temperature=0.7)
    agent = LLMAgent(llm)
    app = build_graph(agent, rng)

    config = {
        "recursion_limit": 200,
        "run_name": "werewolf-self-play",
        "metadata": {"model": model_name, "num_players": len(game.players)},
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


if __name__ == "__main__":
    main()
