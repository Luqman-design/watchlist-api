"""Din personlige anime-watchlist."""


def find_anime(watchlist: list[dict], title: str) -> dict | None:
    """Find en anime på listen. Ignorerer store og små bogstaver."""
    for anime in watchlist:
        if anime["title"].lower() == title.lower():
            return anime
    return None


def add_anime(watchlist: list[dict], title: str) -> None:
    """Tilføj en anime med status 'planned'."""
    if find_anime(watchlist, title) is not None:
        raise ValueError(f"{title} står allerede på listen")
    watchlist.append({"title": title, "status": "planned", "score": None})


def remove_anime(watchlist: list[dict], title: str) -> None:
    """Fjern en anime fra listen."""
    anime = find_anime(watchlist, title)
    if anime is None:
        raise ValueError(f"{title} er ikke på listen")
    watchlist.remove(anime)


def mark_watched(watchlist: list[dict], title: str) -> None:
    """Sæt status til 'watched'."""
    anime = find_anime(watchlist, title)
    if anime is None:
        raise ValueError(f"{title} er ikke på listen")
    anime["status"] = "watched"


def rate_anime(watchlist: list[dict], title: str, score: int) -> None:
    """Giv en karakter fra 1 til 10. Kun for sete anime."""
    anime = find_anime(watchlist, title)
    if anime is None:
        raise ValueError(f"{title} er ikke på listen")
    if anime["status"] != "watched":
        raise ValueError(f"{title} er ikke set endnu, så den kan ikke få en karakter")
    if score < 1 or score > 10:
        raise ValueError(f"Karakteren skal være fra 1 til 10, ikke {score}")
    anime["score"] = score