import httpx


class MangaFlixSource:
    name = "MangaFlix"
    api_url = "https://api.mangaflix.net/v1"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    async def details(self, manga_id: str):
        url = f"{self.api_url}/mangas/{manga_id}"

        async with httpx.AsyncClient(headers=self.headers, timeout=60) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return None

            data = r.json().get("data", {})

        type_raw = str(data.get("type", "")).lower()
        manga_type = "Manhwa" if "manhwa" in type_raw else "Manga"

        chapters = [
            {
                "chapter_number": ch.get("number"),
                "url": ch.get("_id"),
            }
            for ch in data.get("chapters", [])
        ]

        return {
            "title": data.get("name"),
            "type": manga_type,
            "cover": data.get("poster", {}).get("default_url"),
            "chapters": chapters,
            "source": self
        }

    async def pages(self, chapter_id: str):
        url = f"{self.api_url}/chapters/{chapter_id}?selected_language=pt-br"

        async with httpx.AsyncClient(headers=self.headers, timeout=60) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return []

            data = r.json()

        return [
            img.get("default_url")
            for img in data.get("data", {}).get("images", [])
            if img.get("default_url")
        ]
