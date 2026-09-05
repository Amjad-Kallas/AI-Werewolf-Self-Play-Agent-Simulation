import random

from langchain_ollama import ChatOllama

from ai_werewolf.engine.setup import new_game
from ai_werewolf.graph.build import build_graph
from ai_werewolf.llm.agent import LLMAgent

DEFAULT_NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank"]


def main() -> None:
    rng = random.Random()
    game = new_game(DEFAULT_NAMES, num_werewolves=2, rng=rng)

    llm = ChatOllama(model="qwen2.5:3b", temperature=0.7)
    agent = LLMAgent(llm)
    app = build_graph(agent, rng)

    result = app.invoke({"game": game, "discussion": []}, config={"recursion_limit": 200})
    final_game = result["game"]

    roles = ", ".join(f"{p.name}={p.role.value}" for p in final_game.players)
    print(f"Roles: {roles}\n")
    print("\n".join(final_game.log))
    print(f"\nWinner: {final_game.winner.value}")


if __name__ == "__main__":
    main()
