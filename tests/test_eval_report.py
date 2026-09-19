import pandas as pd

from ai_werewolf.eval_report import build_report


def make_row(provider, num_players, num_werewolves, winner, rounds_played, werewolves_caught, seer_present=True, seer_investigations=2, seer_correct_identifications=1):
    return {
        "provider": provider,
        "num_players": num_players,
        "num_werewolves": num_werewolves,
        "winner": winner,
        "rounds_played": rounds_played,
        "werewolves_caught": werewolves_caught,
        "seer_present": seer_present,
        "seer_investigations": seer_investigations,
        "seer_correct_identifications": seer_correct_identifications,
    }


def test_report_separates_different_player_counts_for_the_same_provider():
    df = pd.DataFrame(
        [
            make_row("mistral", 6, 2, "werewolves", 2, 0),
            make_row("mistral", 6, 2, "werewolves", 1, 0),
            make_row("mistral", 8, 2, "villagers", 3, 2),
        ]
    )

    report = build_report(df)

    assert "mistral, 6p/2w (2 games)" in report
    assert "mistral, 8p/2w (1 games)" in report
    # the 8p cohort's 100% villager win rate must not be averaged into the 6p cohort
    six_p_section = report.split("6p/2w")[1].split("8p/2w")[0]
    assert "werewolves win rate: 100%" in six_p_section


def test_report_computes_seer_accuracy_and_caught_rate():
    df = pd.DataFrame(
        [
            make_row("ollama", 6, 2, "werewolves", 2, 1, seer_investigations=4, seer_correct_identifications=2),
            make_row("ollama", 6, 2, "villagers", 2, 2, seer_investigations=4, seer_correct_identifications=2),
        ]
    )

    report = build_report(df)

    assert "werewolves caught (of those in play): 75%" in report  # avg of 1/2=50% and 2/2=100%
    assert "seer investigation accuracy: 4/8 (50%)" in report


def test_report_handles_games_with_no_seer():
    df = pd.DataFrame([make_row("ollama", 6, 2, "werewolves", 2, 0, seer_present=False, seer_investigations=0, seer_correct_identifications=0)])

    report = build_report(df)

    assert "seer investigation accuracy" not in report
