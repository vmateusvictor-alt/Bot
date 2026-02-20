import httpx


class ToonBrSource:
    name = "ToonBr"
    api_url = "https://api.toonbr.com"

    async def search(self, query: str):
        url = f"{self.api_url}/api/manga?page=1&limit=20&search={query}"

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
            except:
                return []

        return [
            {"title": m.get("title"), "url": m.get("slug")}
            for m in data.get("data", [])
        ]

    async def details(self, manga_slug: str):
        url = f"{self.api_url}/api/manga/{manga_slug}"

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
            except:
                return None

        status = str(data.get("status", "")).lower()
        if "complete" not in status:
            return None

        manga_type = "Manhwa" if "manhwa" in str(data.get("type", "")).lower() else "Manga"

        chapters = [
            {
                "chapter_number": ch.get("chapterNumber"),
                "url": ch.get("id"),
            }
            for ch in data.get("chapters", [])
        ]

        return {
            "title": data.get("title"),
            "status": "completed",
            "type": manga_type,
            "cover": data.get("cover"),
            "chapters": chapters,
            "source": self
        }

    async def pages(self, chapter_id: str):
        url = f"{self.api_url}/api/chapter/{chapter_id}"

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
            except:
                return []

        return [
            p.get("imageUrl")
            for p in data.get("pages", [])
            if p.get("imageUrl")
        ]
