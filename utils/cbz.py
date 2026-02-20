import os
import zipfile
import httpx

os.makedirs("tmp", exist_ok=True)


async def create_volume_cbz(source, volume, manga_title, vol_number):
    safe_title = manga_title.replace("/", "").replace(" ", "_")
    filename = f"{safe_title}_Vol_{vol_number}.cbz"
    path = os.path.join("tmp", filename)

    with zipfile.ZipFile(path, "w") as cbz:
        index = 1

        async with httpx.AsyncClient(timeout=60) as client:
            for chapter in volume:
                pages = await source.pages(chapter["url"])

                for img_url in pages:
                    try:
                        r = await client.get(img_url)
                        if r.status_code == 200:
                            cbz.writestr(f"{index}.jpg", r.content)
                            index += 1
                    except:
                        continue

    return path, filename
