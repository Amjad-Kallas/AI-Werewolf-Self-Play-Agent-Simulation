import argparse

import pandas as pd

from ai_werewolf.evaluation import RESULTS_PATH


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize eval/results.csv for reporting.")
    parser.add_argument("--path", default=str(RESULTS_PATH))
    return parser.parse_args()


def build_report(df: pd.DataFrame) -> str:
    lines = [f"Games recorded: {len(df)}"]

    group_cols = ["provider", "num_players", "num_werewolves"]
    for (provider, num_players, num_werewolves), group in df.groupby(group_cols):
        label = f"{provider}, {num_players}p/{num_werewolves}w"
        lines.append(f"\n== {label} ({len(group)} games) ==")
        win_rate = group["winner"].value_counts(normalize=True)
        for team, rate in win_rate.items():
            lines.append(f"  {team} win rate: {rate:.0%}")

        caught_rate = (group["werewolves_caught"] / group["num_werewolves"]).mean()
        lines.append(f"  werewolves caught (of those in play): {caught_rate:.0%}")
        lines.append(f"  average rounds played: {group['rounds_played'].mean():.1f}")

        with_seer = group[group["seer_present"]]
        if len(with_seer):
            investigations = with_seer["seer_investigations"].sum()
            correct = with_seer["seer_correct_identifications"].sum()
            accuracy = correct / investigations if investigations else float("nan")
            lines.append(f"  seer investigation accuracy: {correct}/{investigations} ({accuracy:.0%})")

    return "\n".join(lines)


def main() -> None:
    args = _parse_args()
    df = pd.read_csv(args.path)
    print(build_report(df))


if __name__ == "__main__":
    main()
