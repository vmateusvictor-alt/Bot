from sources.toonbr import ToonBrSource


async def get_all_by_genre(genre_name: str):
    source = ToonBrSource()

    results = await source.get_by_category(genre_name)

    mangas = []
    manhwas = []

    for item in results:
        details = await source.details(item["slug"])
        if not details:
            continue

        if details["type"] == "Manhwa":
            manhwas.append(details)
        else:
            mangas.append(details)

    return mangas, manhwas
