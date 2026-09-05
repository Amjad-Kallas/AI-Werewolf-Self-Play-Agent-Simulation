from ai_werewolf.engine.voting import tally_votes


def test_clear_majority_eliminated():
    votes = {0: 2, 1: 2, 2: 0}
    assert tally_votes(votes) == 2


def test_tie_returns_none():
    votes = {0: 1, 1: 0}
    assert tally_votes(votes) is None


def test_three_way_tie_returns_none():
    votes = {0: 1, 1: 2, 2: 0}
    assert tally_votes(votes) is None


def test_no_votes_returns_none():
    assert tally_votes({}) is None


def test_single_vote_wins():
    assert tally_votes({0: 5}) == 5
