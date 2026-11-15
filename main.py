"""Watchlist API: din anime-watchlist som en web-service."""
from pathlib import Path

from fastapi import FastAPI

import anime_api
from storage import load_watchlist

WATCHLIST_PATH = Path("watchlist.json")

app = FastAPI(title="Watchlist API")


@app.get("/watchlist")
def get_watchlist():
    return load_watchlist(WATCHLIST_PATH)


@app.get("/search")
def search(q: str):
    return anime_api.search_anime(q)
"""Det er hele hemmeligheden: en adresse og en metode kobles til en almindelig Python-funktion. 
Resten klarer FastAPI."""

    