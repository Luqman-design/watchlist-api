"""Watchlist API: din anime-watchlist som en web-service."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import anime_api
from storage import load_watchlist, save_watchlist
from watchlist import add_anime, find_anime, mark_watched, rate_anime, remove_anime

WATCHLIST_PATH = Path("watchlist.json")

app = FastAPI(title="Watchlist API")


# --- Hvordan data i en request skal se ud ---

class NewAnime(BaseModel):
    title: str


class AnimeUpdate(BaseModel):
    watched: bool = False       # sæt til true for at markere som set
    score: int | None = None    # karakter fra 1 til 10


# --- Hjælper ---

def get_existing_anime(watchlist: list[dict], title: str) -> dict:
    """Find en anime, eller svar med 404, hvis den ikke er på listen."""
    anime = find_anime(watchlist, title)
    if anime is None:
        raise HTTPException(status_code=404, detail=f"{title} er ikke på listen")
    return anime


# --- Endpoints ---

@app.get("/watchlist")
def get_watchlist():
    """Hent hele watchlisten."""
    return load_watchlist(WATCHLIST_PATH)


@app.post("/watchlist", status_code=201)
def add_to_watchlist(anime: NewAnime):
    """Tilføj en anime. Svarer 409, hvis den allerede står der."""
    watchlist = load_watchlist(WATCHLIST_PATH)
    if find_anime(watchlist, anime.title) is not None:
        raise HTTPException(status_code=409, detail=f"{anime.title} står allerede på listen")
    add_anime(watchlist, anime.title)
    save_watchlist(watchlist, WATCHLIST_PATH)
    return watchlist


@app.patch("/watchlist/{title}")
def update_anime(title: str, update: AnimeUpdate):
    """Markér som set og/eller giv en karakter."""
    watchlist = load_watchlist(WATCHLIST_PATH)
    get_existing_anime(watchlist, title)

    if update.watched:
        mark_watched(watchlist, title)
    if update.score is not None:
        try:
            rate_anime(watchlist, title, update.score)
        except ValueError as e:
            # fx karakter 15, eller karakter til en anime, der ikke er set
            raise HTTPException(status_code=400, detail=str(e))

    save_watchlist(watchlist, WATCHLIST_PATH)
    return find_anime(watchlist, title)


@app.delete("/watchlist/{title}")
def delete_anime(title: str):
    """Fjern en anime fra listen."""
    watchlist = load_watchlist(WATCHLIST_PATH)
    get_existing_anime(watchlist, title)
    remove_anime(watchlist, title)
    save_watchlist(watchlist, WATCHLIST_PATH)
    return watchlist


@app.get("/search")
def search(q: str):
    """Søg efter anime i AniList."""
    return anime_api.search_anime(q)


@app.get("/season")
def season():
    """De mest populære anime i den nuværende sæson."""
    return anime_api.current_season()