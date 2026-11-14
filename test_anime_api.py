from datetime import date

import pytest
import requests

import anime_api

FAKE_FRIEREN = {
    "title": {"romaji": "Sousou no Frieren", "english": "Frieren: Beyond Journey's End"},
    "averageScore": 93,
    "episodes": 28,
    "seasonYear": 2023,
    "genres": ["Adventure", "Drama", "Fantasy"],
}


class FakeResponse:
    """Et falsk svar, der lader som om, det kom fra AniList."""

    def __init__(self, media, status_code=200):
        self._media = media
        self.status_code = status_code

    def json(self):
        return {"data": {"Page": {"media": self._media}}}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"Status {self.status_code}")


def test_search_returns_simplified_results(monkeypatch):
    monkeypatch.setattr(anime_api.requests, "post", lambda *a, **kw: FakeResponse([FAKE_FRIEREN]))

    results = anime_api.search_anime("frieren")

    assert results == [{
        "title": "Sousou no Frieren",
        "title_english": "Frieren: Beyond Journey's End",
        "score": 9.3,
        "episodes": 28,
        "year": 2023,
        "genres": ["Adventure", "Drama", "Fantasy"],
    }]


def test_search_sends_query_to_api(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json["variables"]))
        return FakeResponse([])

    monkeypatch.setattr(anime_api.requests, "post", fake_post)

    anime_api.search_anime("vinland saga", limit=3)

    assert calls == [("https://graphql.anilist.co", {"search": "vinland saga", "perPage": 3})]


def test_search_with_no_results_gives_empty_list(monkeypatch):
    monkeypatch.setattr(anime_api.requests, "post", lambda *a, **kw: FakeResponse([]))
    assert anime_api.search_anime("findes ikke") == []


def test_missing_fields_do_not_crash(monkeypatch):
    monkeypatch.setattr(anime_api.requests, "post", lambda *a, **kw: FakeResponse([{"title": {"romaji": "Ukendt"}}]))
    result = anime_api.search_anime("ukendt")[0]
    assert result["title"] == "Ukendt"
    assert result["genres"] == []
    assert result["score"] is None


def test_api_error_is_raised(monkeypatch):
    monkeypatch.setattr(anime_api.requests, "post", lambda *a, **kw: FakeResponse([], status_code=500))
    with pytest.raises(requests.HTTPError):
        anime_api.search_anime("frieren")


@pytest.mark.parametrize("day, season", [
    (date(2026, 1, 1), "WINTER"),
    (date(2026, 3, 31), "WINTER"),
    (date(2026, 4, 1), "SPRING"),
    (date(2026, 6, 30), "SPRING"),
    (date(2026, 7, 1), "SUMMER"),
    (date(2026, 9, 30), "SUMMER"),
    (date(2026, 10, 1), "FALL"),
    (date(2026, 12, 31), "FALL"),
])
def test_season_for_boundaries(day, season):
    assert anime_api.season_for(day) == season


def test_current_season_asks_for_this_season(monkeypatch):
    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append(json["variables"])
        return FakeResponse([FAKE_FRIEREN])

    monkeypatch.setattr(anime_api.requests, "post", fake_post)

    results = anime_api.current_season(limit=5)

    today = date.today()
    assert calls == [{"season": anime_api.season_for(today), "year": today.year, "perPage": 5}]
    assert results[0]["title"] == "Sousou no Frieren"