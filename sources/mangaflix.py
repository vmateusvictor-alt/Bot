import httpx


class MangaFlixSource:
    name = "MangaFlix"
    api_url = "https://api.mangaflix.net/v1"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    timeout = httpx.Timeout(60.0)

    async def search(self, query: str):
        url = f"{self.api_url}/search/mangas"
        params = {"query": query, "selected_language": "pt-br"}

        async with httpx.AsyncClient(headers=self.headers) as client:
            r = await client.get(url, params=params)
            if r.status_code != 200:
                return []

            data = r.json()

        return [
            {"title": m.get("name"), "url": m.get("_id")}
            for m in data.get("data", [])
        ]

    async def details(self, manga_id: str):
        url = f"{self.api_url}/mangas/{manga_id}"

        async with httpx.AsyncClient(headers=self.headers) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return None

            data = r.json().get("data", {})

        status = str(data.get("status", "")).lower()
        if "complete" not in status:
            return None

        manga_type = "Manhwa" if "manhwa" in str(data.get("type", "")).lower() else "Manga"

        chapters = [
            {
                "chapter_number": ch.get("number"),
                "url": ch.get("_id"),
            }
            for ch in data.get("chapters", [])
        ]

        return {
            "title": data.get("name"),
            "status": "completed",
            "type": manga_type,
            "cover": data.get("cover_url"),
            "chapters": chapters,
            "source": self
        }

    async def pages(self, chapter_id: str):
        url = f"{self.api_url}/chapters/{chapter_id}"

        async with httpx.AsyncClient(headers=self.headers) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return []

            data = r.json()

        return [
            img.get("default_url")
            for img in data.get("data", {}).get("images", [])
            if img.get("default_url")
      ]
