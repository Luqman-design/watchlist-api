import pytest

from watchlist import add_anime, find_anime, mark_watched, rate_anime, remove_anime


@pytest.fixture
def watchlist():
    """En lille watchlist, som hver test får sin egen friske kopi af."""
    liste = []
    add_anime(liste, "Frieren")
    add_anime(liste, "Vinland Saga")
    mark_watched(liste, "Vinland Saga")
    return liste


# --- find_anime ---

def test_find_ignores_upper_and_lower_case(watchlist):
    assert find_anime(watchlist, "FRIEREN")["title"] == "Frieren"


def test_find_returns_none_when_missing(watchlist):
    assert find_anime(watchlist, "Naruto") is None


# --- add_anime (regel 1) ---

def test_add_puts_anime_on_list_as_planned():
    liste = []
    add_anime(liste, "Frieren")
    assert liste == [{"title": "Frieren", "status": "planned", "score": None}]


def test_add_same_anime_twice_raises_error(watchlist):
    with pytest.raises(ValueError):
        add_anime(watchlist, "frieren")


# --- remove_anime (regel 2) ---

def test_remove_takes_anime_off_list(watchlist):
    remove_anime(watchlist, "frieren")
    assert find_anime(watchlist, "Frieren") is None
    assert len(watchlist) == 1


def test_remove_missing_anime_raises_error(watchlist):
    with pytest.raises(ValueError):
        remove_anime(watchlist, "Naruto")


# --- mark_watched (regel 2) ---

def test_mark_watched_changes_status_without_duplicate(watchlist):
    mark_watched(watchlist, "frieren")
    assert find_anime(watchlist, "Frieren")["status"] == "watched"
    assert len(watchlist) == 2


def test_mark_watched_missing_anime_raises_error(watchlist):
    with pytest.raises(ValueError):
        mark_watched(watchlist, "Naruto")


# --- rate_anime (regel 2, 3 og 4) ---

@pytest.mark.parametrize("score", [1, 10])
def test_rate_accepts_boundary_scores(watchlist, score):
    rate_anime(watchlist, "Vinland Saga", score)
    assert find_anime(watchlist, "Vinland Saga")["score"] == score


@pytest.mark.parametrize("score", [0, 11, -5])
def test_rate_rejects_scores_outside_1_to_10(watchlist, score):
    with pytest.raises(ValueError):
        rate_anime(watchlist, "Vinland Saga", score)


def test_rate_unwatched_anime_raises_error(watchlist):
    with pytest.raises(ValueError):
        rate_anime(watchlist, "Frieren", 8)


def test_rate_missing_anime_raises_error(watchlist):
    with pytest.raises(ValueError):
        rate_anime(watchlist, "Naruto", 8)