import httpx
from utils.loader import get_all_sources

MANGAFLIX_API = "https://api.mangaflix.net/v1"


async def get_genre_id(genre_name: str):
    url = f"{MANGAFLIX_API}/genres?include_adult=true&selected_language=pt-br"

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url)
        if r.status_code != 200:
            return None

        data = r.json()

    for g in data.get("data", []):
        if genre_name.lower() in g.get("name", "").lower():
            return g.get("_id")

    return None


async def get_all_by_genre(genre_name: str):
    genre_id = await get_genre_id(genre_name)
    if not genre_id:
        return [], []

    mangas = []
    manhwas = []

    offset = 0
    limit = 20

    source = get_all_sources()["MangaFlix"]

    async with httpx.AsyncClient(timeout=60) as client:
        while True:
            url = f"{MANGAFLIX_API}/genres/{genre_id}/mangas"
            params = {
                "offset": offset,
                "limit": limit,
                "include_adult": "true"
            }

            r = await client.get(url, params=params)
            if r.status_code != 200:
                break

            data = r.json()
            items = data.get("data", [])

            if not items:
                break

            for item in items:
                manga_id = item.get("_id")

                details = await source.details(manga_id)
                if not details:
                    continue

                if details["type"] == "Manhwa":
                    manhwas.append(details)
                else:
                    mangas.append(details)

            offset += limit

    return mangas, manhwas
