"""One-off doc-generation script: turn eval/results.csv into README charts.

Not part of the shipped package - matplotlib is intentionally not a project
dependency, so run this via `uv run --with matplotlib python scripts/generate_eval_charts.py`.
"""

import matplotlib.pyplot as plt
import pandas as pd

RESULTS_PATH = "eval/results.csv"
OUT_DIR = "docs/images"


def config_label(row) -> str:
    return f"{row['provider']}\n{row['num_players']}p/{row['num_werewolves']}w"


def plot_win_rates(df: pd.DataFrame) -> None:
    grouped = df.groupby(["provider", "num_players", "num_werewolves"])
    labels, villager_rates, werewolf_rates = [], [], []
    for (provider, num_players, num_werewolves), group in grouped:
        counts = group["winner"].value_counts(normalize=True)
        labels.append(f"{provider}\n{num_players}p/{num_werewolves}w")
        villager_rates.append(counts.get("villagers", 0) * 100)
        werewolf_rates.append(counts.get("werewolves", 0) * 100)

    x = range(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([i - width / 2 for i in x], villager_rates, width, label="Villagers", color="#4C72B0")
    ax.bar([i + width / 2 for i in x], werewolf_rates, width, label="Werewolves", color="#C44E52")
    ax.set_ylabel("Win rate (%)")
    ax.set_title("Win rate by provider and player/werewolf ratio")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_ylim(0, 105)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/win_rates.png", dpi=150)
    print(f"saved {OUT_DIR}/win_rates.png")


def plot_seer_accuracy(df: pd.DataFrame) -> None:
    grouped = df[df["seer_present"]].groupby(["provider", "num_players", "num_werewolves"])
    labels, accuracy, baseline = [], [], []
    for (provider, num_players, num_werewolves), group in grouped:
        investigations = group["seer_investigations"].sum()
        correct = group["seer_correct_identifications"].sum()
        labels.append(f"{provider}\n{num_players}p/{num_werewolves}w")
        accuracy.append((correct / investigations * 100) if investigations else 0)
        baseline.append(num_werewolves / num_players * 100)

    x = range(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([i - width / 2 for i in x], accuracy, width, label="Actual Seer accuracy", color="#55A868")
    ax.bar([i + width / 2 for i in x], baseline, width, label="Random-guess baseline", color="#8C8C8C")
    ax.set_ylabel("Correct werewolf identifications (%)")
    ax.set_title("Seer investigation accuracy vs. random baseline")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_ylim(0, max(accuracy + baseline) * 1.3)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/seer_accuracy.png", dpi=150)
    print(f"saved {OUT_DIR}/seer_accuracy.png")


def main() -> None:
    df = pd.read_csv(RESULTS_PATH)
    plot_win_rates(df)
    plot_seer_accuracy(df)


if __name__ == "__main__":
    main()
