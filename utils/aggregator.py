import asyncio
from utils.loader import get_all_sources


def normalize_type(raw_type):
    raw_type = str(raw_type).lower()
    if "manhwa" in raw_type:
        return "Manhwa"
    return "Manga"


async def get_all_completed():
    sources = get_all_sources()
    unique = {}

    for name, source in sources.items():
        try:
            results = await source.search("")
        except:
            continue

        for manga in results:
            try:
                details = await source.details(manga["url"])
                if not details:
                    continue

                if details["status"] != "completed":
                    continue

                key = details["title"].strip().lower()

                if key not in unique:
                    unique[key] = details

            except:
                continue

    mangas = [m for m in unique.values() if m["type"] == "Manga"]
    manhwas = [m for m in unique.values() if m["type"] == "Manhwa"]

    return mangas, manhwas
