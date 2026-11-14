"""Gem og indlæs watchlisten fra en JSON-fil på disken."""
import json
from pathlib import Path

DEFAULT_PATH = Path("watchlist.json")


def load_watchlist(path: Path = DEFAULT_PATH) -> list[dict]:
    """Læs watchlisten fra filen. Findes filen ikke endnu, startes med en tom liste."""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_watchlist(watchlist: list[dict], path: Path = DEFAULT_PATH) -> None:
    """Gem watchlisten i filen, så den kan læses igen næste gang."""
    path.write_text(json.dumps(watchlist, indent=2, ensure_ascii=False), encoding="utf-8")
