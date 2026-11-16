# watchlist-api

![CI/CD](https://github.com/Luqman-design/watchlist-api/actions/workflows/ci-cd.yml/badge.svg)

Et lille REST API til en personlig anime-watchlist, bygget med FastAPI. Det kan tilføje, opdatere og fjerne anime på listen og slå rigtige anime op via AniList.

Projektet er lavet for at lære, hvordan et web-API bygges i praksis, og hvordan man pakker det i Docker og udgiver det automatisk med en CI/CD-pipeline.

## Endpoints

| Endpoint | Gør | Statuskoder |
|---|---|---|
| `GET /watchlist` | Henter listen | 200 |
| `POST /watchlist` | Tilføjer en anime | 201, 409 findes allerede, 422 mangler titel |
| `PATCH /watchlist/{title}` | Markerer som set og/eller giver karakter (1-10) | 200, 400 ugyldig karakter, 404 findes ikke |
| `DELETE /watchlist/{title}` | Fjerner en anime | 200, 404 findes ikke |
| `GET /search?q=...` | Søger efter anime i AniList | 200, 422 mangler `q` |
| `GET /season` | De mest populære anime i den nuværende sæson | 200 |

Når serveren kører, findes en interaktiv dokumentation på `/docs`, hvor alle endpoints kan afprøves.

Eksempel:

```bash
curl -X POST http://localhost:8000/watchlist -H "Content-Type: application/json" -d '{"title": "Frieren"}'
curl -X PATCH http://localhost:8000/watchlist/frieren -H "Content-Type: application/json" -d '{"watched": true, "score": 9}'
curl http://localhost:8000/watchlist
```

## Kør det

**Med Docker**, direkte fra GitHubs container-registry:

```bash
docker run -p 8000:8000 ghcr.io/luqman-design/watchlist-api:latest
```

**Eller byg selv:**

```bash
docker build -t watchlist-api .
docker run -p 8000:8000 watchlist-api
```

**Eller uden Docker:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Gå derefter til http://localhost:8000/docs.

## Tests

```bash
pytest
```

46 tests dækker reglerne for watchlisten, gem og indlæs, AniList-opslaget (med falske svar, så testene ikke afhænger af internettet) og alle endpoints, inklusive fejlkoderne.

## CI/CD

Ved hvert push og pull request mod `main` kører GitHub Actions to jobs:

1. **test**: installerer pakkerne og kører alle tests på en frisk maskine
2. **docker**: kun ved push til `main` og kun hvis testene er grønne. Bygger Docker-imaget og udgiver det på `ghcr.io` med to tags: `latest` og commit-id'et

## Struktur

- `main.py`: API'et og alle endpoints
- `watchlist.py`: reglerne for watchlisten
- `storage.py`: gemmer og indlæser listen i `watchlist.json`
- `anime_api.py`: klient til AniLists GraphQL-API
- `Dockerfile`: opskriften på containeren
- `.github/workflows/ci-cd.yml`: pipelinen

Logikken i `watchlist.py`, `storage.py` og `anime_api.py` er genbrugt fra mit tidligere projekt, en anime-agent. Kun rammen omkring er ny.

## Hvad jeg har lært

- **Et API er en bagende uden brugerflade.** Det er beregnet til, at andre programmer kalder det. `/docs` er et testværktøj, ikke produktet.
- **Min server er både server og klient.** Den svarer på requests fra browseren og sender selv requests videre til AniList.
- **Fejl skal oversættes til HTTP.** Når en regel brydes, fx karakter 15, svarer API'et med en passende statuskode og en forklaring i stedet for at crashe.
- **En container glemmer sine data.** Watchlisten gemmes inde i containeren og forsvinder, når den stoppes. Løsningen er et volume, men det har jeg ikke brugt endnu.
- **Rækkefølgen i en Dockerfile betyder noget.** Fordi pakkerne installeres før koden kopieres ind, kan Docker genbruge det trin, når kun koden ændrer sig.
- **En pipeline kan fejle, før den overhovedet starter.** Min første kørsel fejlede på 0 sekunder, fordi indrykningen i yml-filen var forkert.

## Næste skridt

- Gemme data uden for containeren med et volume eller en database
- Hoste API'et på en server, så det kan nås fra internettet
- En lille hjemmeside, der bruger API'et
