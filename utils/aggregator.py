from utils.loader import get_all_sources


def normalize_type(raw_type):
    raw_type = str(raw_type).lower()
    if "manhwa" in raw_type:
        return "Manhwa"
    return "Manga"


async def search_completed(query: str):
    sources = get_all_sources()
    unique = {}

    for source_name, source in sources.items():
        try:
            results = await source.search(query)
        except Exception:
            continue

        for manga in results:
            try:
                details = await source.details(manga["url"])
                if not details:
                    continue

                if details.get("status") != "completed":
                    continue

                key = details["title"].strip().lower()

                if key not in unique:
                    unique[key] = details

            except Exception:
                continue

    return list(unique.values())
