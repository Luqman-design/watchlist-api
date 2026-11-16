import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def temp_watchlist(tmp_path, monkeypatch):
    """Hver test får sin egen tomme watchlist-fil, så den rigtige ikke røres."""
    monkeypatch.setattr(main, "WATCHLIST_PATH", tmp_path / "watchlist.json")


def add(title):
    return client.post("/watchlist", json={"title": title})


# --- GET /watchlist ---

def test_get_empty_watchlist():
    response = client.get("/watchlist")
    assert response.status_code == 200
    assert response.json() == []


# --- POST /watchlist ---

def test_post_adds_anime_and_returns_201():
    response = add("Frieren")
    assert response.status_code == 201
    assert client.get("/watchlist").json() == [{"title": "Frieren", "status": "planned", "score": None}]


def test_post_duplicate_gives_409():
    add("Frieren")
    response = add("frieren")
    assert response.status_code == 409


def test_post_without_title_gives_422():
    response = client.post("/watchlist", json={})
    assert response.status_code == 422


# --- PATCH /watchlist/{title} ---

def test_patch_marks_watched_and_rates():
    add("Frieren")
    response = client.patch("/watchlist/frieren", json={"watched": True, "score": 9})
    assert response.status_code == 200
    assert response.json() == {"title": "Frieren", "status": "watched", "score": 9}


def test_patch_score_on_unwatched_gives_400():
    add("Frieren")
    response = client.patch("/watchlist/Frieren", json={"score": 9})
    assert response.status_code == 400


@pytest.mark.parametrize("score", [0, 11])
def test_patch_invalid_score_gives_400(score):
    add("Frieren")
    response = client.patch("/watchlist/Frieren", json={"watched": True, "score": score})
    assert response.status_code == 400


def test_patch_missing_anime_gives_404():
    response = client.patch("/watchlist/Naruto", json={"watched": True})
    assert response.status_code == 404


# --- DELETE /watchlist/{title} ---

def test_delete_removes_anime():
    add("Frieren")
    add("Vinland Saga")
    response = client.delete("/watchlist/frieren")
    assert response.status_code == 200
    assert [a["title"] for a in client.get("/watchlist").json()] == ["Vinland Saga"]


def test_delete_missing_anime_gives_404():
    response = client.delete("/watchlist/Naruto")
    assert response.status_code == 404


# --- GET /search og /season ---

def test_search_returns_results(monkeypatch):
    monkeypatch.setattr(main.anime_api, "search_anime", lambda q: [{"title": f"Fundet: {q}"}])
    response = client.get("/search", params={"q": "frieren"})
    assert response.status_code == 200
    assert response.json() == [{"title": "Fundet: frieren"}]


def test_search_without_query_gives_422():
    assert client.get("/search").status_code == 422


def test_season_returns_results(monkeypatch):
    monkeypatch.setattr(main.anime_api, "current_season", lambda: [{"title": "Blue Box"}])
    assert client.get("/season").json() == [{"title": "Blue Box"}]