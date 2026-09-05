import random
from collections import Counter


def tally_votes(votes: dict[int, int]) -> int | None:
    """Return the eliminated player id, or None if there's a tie for the lead.

    `votes` maps voter_id -> target_id. Abstentions are simply absent keys.
    """
    if not votes:
        return None

    counts = Counter(votes.values())
    top_count = max(counts.values())
    leaders = [target for target, count in counts.items() if count == top_count]

    if len(leaders) > 1:
        return None
    return leaders[0]


def tally_votes_with_tiebreak(votes: dict[int, int], rng: random.Random) -> int:
    """Like `tally_votes`, but a tie is broken randomly instead of returning None.

    Used where a decision must be made no matter what (e.g. the werewolves'
    nightly kill), unlike the day vote where a tie means no elimination.
    """
    if not votes:
        raise ValueError("no votes to tally")

    counts = Counter(votes.values())
    top_count = max(counts.values())
    leaders = [target for target, count in counts.items() if count == top_count]
    return rng.choice(leaders)
