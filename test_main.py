import pytest
from fastapi.testclient import TestClient

import main
from storage import save_watchlist

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def temp_watchlist(tmp_path, monkeypatch):
    """Hver test får sin egen tomme watchlist-fil, så den rigtige ikke røres."""
    monkeypatch.setattr(main, "WATCHLIST_PATH", tmp_path / "watchlist.json")


def test_get_empty_watchlist():
    response = client.get("/watchlist")
    assert response.status_code == 200
    assert response.json() == []


def test_get_watchlist_with_anime():
    save_watchlist([{"title": "Frieren", "status": "planned", "score": None}], main.WATCHLIST_PATH)
    response = client.get("/watchlist")
    assert response.json()[0]["title"] == "Frieren"


def test_search_returns_results(monkeypatch):
    monkeypatch.setattr(main.anime_api, "search_anime", lambda q: [{"title": f"Fundet: {q}"}])
    response = client.get("/search", params={"q": "frieren"})
    assert response.status_code == 200
    assert response.json() == [{"title": "Fundet: frieren"}]


def test_search_without_query_gives_422():
    response = client.get("/search")
    assert response.status_code == 422
