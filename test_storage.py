from storage import load_watchlist, save_watchlist
from watchlist import add_anime, mark_watched


def test_load_returns_empty_list_when_file_missing(tmp_path):
    assert load_watchlist(tmp_path / "findes_ikke.json") == []


def test_save_then_load_gives_same_watchlist(tmp_path):
    path = tmp_path / "watchlist.json"
    liste = []
    add_anime(liste, "Frieren")
    add_anime(liste, "Shingeki no Kyojin")
    mark_watched(liste, "Frieren")

    save_watchlist(liste, path)

    assert load_watchlist(path) == liste


def test_special_characters_survive_save_and_load(tmp_path):
    path = tmp_path / "watchlist.json"
    liste = []
    add_anime(liste, "葬送のフリーレン")
    add_anime(liste, "Æblegrød på månen")

    save_watchlist(liste, path)

    assert load_watchlist(path) == liste