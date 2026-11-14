"""Opslag i en rigtig anime-database via det gratis AniList-API."""
from datetime import date

import requests

API_URL = "https://graphql.anilist.co"

# Hvilke felter vi vil have tilbage for hver anime
FIELDS = """
    title { romaji english }
    averageScore
    episodes
    seasonYear
    genres
"""

SEARCH_QUERY = f"""
query ($search: String, $perPage: Int) {{
  Page(perPage: $perPage) {{
    media(search: $search, type: ANIME) {{ {FIELDS} }}
  }}
}}
"""

SEASON_QUERY = f"""
query ($season: MediaSeason, $year: Int, $perPage: Int) {{
  Page(perPage: $perPage) {{
    media(season: $season, seasonYear: $year, type: ANIME, sort: POPULARITY_DESC) {{ {FIELDS} }}
  }}
}}
"""


def _ask_anilist(query: str, variables: dict) -> list[dict]:
    """Send en forespørgsel til AniList, og returnér listen af anime."""
    resp = requests.post(API_URL, json={"query": query, "variables": variables}, timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]["Page"]["media"]


def _simplify(item: dict) -> dict:
    """Skær API'ets svar ned til det, agenten har brug for."""
    title = item.get("title") or {}
    score = item.get("averageScore")
    return {
        "title": title.get("romaji"),
        "title_english": title.get("english"),
        "score": score / 10 if score is not None else None,  # AniList giver 0-100, vi vil have 0-10
        "episodes": item.get("episodes"),
        "year": item.get("seasonYear"),
        "genres": item.get("genres") or [],
    }


def season_for(day: date) -> str:
    """Hvilken anime-sæson en dato hører til."""
    if day.month <= 3:
        return "WINTER"
    if day.month <= 6:
        return "SPRING"
    if day.month <= 9:
        return "SUMMER"
    return "FALL"


def search_anime(query: str, limit: int = 5) -> list[dict]:
    """Søg efter anime på titel."""
    items = _ask_anilist(SEARCH_QUERY, {"search": query, "perPage": limit})
    return [_simplify(item) for item in items]


def current_season(limit: int = 10) -> list[dict]:
    """Hent de mest populære anime i den nuværende sæson."""
    today = date.today()
    variables = {"season": season_for(today), "year": today.year, "perPage": limit}
    items = _ask_anilist(SEASON_QUERY, variables)
    return [_simplify(item) for item in items]