import httpx


class ToonBrSource:
    name = "ToonBr"
    api_url = "https://api.toonbr.com"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    # IDs baseados na extensão que você enviou
    CATEGORIES = {
        "romance": "1572cea3-6b8d-4384-869e-98f13eeb0b72",
        "acao": "9c302e17-a1df-42f7-84f9-8de76bc97afb",
        "aventura": "02aa6ee2-1862-4044-a81c-7417b588d096",
        "comedia": "148ba9b3-1353-430e-ab3d-e845cfb35a77",
        "fantasia": "152d8043-499f-46af-bcb1-fa85d4609b06",
        "drama": "e36a8377-378f-472c-a622-a36ed0de493a",
        "isekai": "7fc49228-f081-4829-bae0-124c72b6d3b1",
        "terror": "b67c12d8-89ae-491a-b902-d616c6d52c49",
    }

    async def get_by_category(self, category_name: str):
        category_id = self.CATEGORIES.get(category_name.lower())
        if not category_id:
            return []

        mangas = []
        page = 1

        async with httpx.AsyncClient(headers=self.headers, timeout=60) as client:
            while True:
                url = f"{self.api_url}/mangas"
                params = {
                    "categoryId": category_id,
                    "page": page
                }

                r = await client.get(url, params=params)

                if r.status_code != 200:
                    break

                data = r.json()
                items = data.get("data", [])

                if not items:
                    break

                for item in items:
                    mangas.append({
                        "id": item["id"],
                        "title": item["title"],
                        "slug": item["slug"],
                        "cover": item.get("coverImage"),
                        "status": item.get("status"),
                        "type": "Manhwa",  # ToonBr é majoritariamente manhwa
                        "source": self
                    })

                page += 1

        return mangas

    async def details(self, slug: str):
        url = f"{self.api_url}/manga/{slug}"

        async with httpx.AsyncClient(headers=self.headers, timeout=60) as client:
            r = await client.get(url)

            if r.status_code != 200:
                return None

            data = r.json()

        chapters = []
        for ch in data.get("chapters", []):
            chapters.append({
                "chapter_number": ch.get("chapterNumber"),
                "url": ch.get("id")
            })

        return {
            "title": data.get("title"),
            "cover": data.get("coverImage"),
            "chapters": chapters,
            "type": "Manhwa",
            "source": self
        }

    async def pages(self, chapter_id: str):
        url = f"{self.api_url}/chapter/{chapter_id}"

        async with httpx.AsyncClient(headers=self.headers, timeout=60) as client:
            r = await client.get(url)

            if r.status_code != 200:
                return []

            data = r.json()

        return [
            page.get("imageUrl")
            for page in data.get("pages", [])
            if page.get("imageUrl")
    ]
