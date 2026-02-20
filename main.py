import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from utils.aggregator import search_completed
from utils.volumes import split_into_volumes
from utils.cbz import create_volume_cbz


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Bot Online!\n\n"
        "Use:\n"
        "/bb3 nome_do_manga\n\n"
        "Exemplo:\n"
        "/bb3 solo leveling"
    )


# ================= BB3 =================

async def bb3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(
            "Use:\n/bb3 nome_do_manga"
        )

    query = " ".join(context.args)

    msg = await update.message.reply_text("🔎 Buscando mangá finalizado...")

    results = await search_completed(query)

    if not results:
        return await msg.edit_text("❌ Nenhum mangá/manhwa finalizado encontrado.")

    # Processa um por vez (seguro pro Railway)
    for manga in results:
        await process_manga(update, manga)

    await msg.delete()


# ================= PROCESSAR MANGA =================

async def process_manga(update: Update, manga: dict):
    title = manga["title"]
    cover = manga.get("cover")
    chapters = manga.get("chapters", [])
    source = manga["source"]
    manga_type = manga["type"]

    if not chapters:
        return

    volumes = split_into_volumes(chapters, 50)

    # Envia capa + infos
    if cover:
        await update.message.reply_photo(
            photo=cover,
            caption=(
                f"📖 {title}\n"
                f"📚 Tipo: {manga_type}\n"
                f"📌 Status: Finalizado\n"
                f"📊 Capítulos: {len(chapters)}\n"
                f"📦 Volumes: {len(volumes)}"
            )
        )
    else:
        await update.message.reply_text(
            f"📖 {title}\n"
            f"📚 Tipo: {manga_type}\n"
            f"📌 Status: Finalizado\n"
            f"📊 Capítulos: {len(chapters)}\n"
            f"📦 Volumes: {len(volumes)}"
        )

    # Envia volumes sequencialmente (anti crash)
    for i, volume in enumerate(volumes, start=1):
        try:
            cbz_path, cbz_name = await create_volume_cbz(
                source, volume, title, i
            )

            await update.message.reply_document(
                document=open(cbz_path, "rb"),
                filename=cbz_name
            )

            os.remove(cbz_path)

            await asyncio.sleep(0.5)

        except Exception:
            continue


# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bb3", bb3))

    print("BOT INICIADO COM SUCESSO")

    app.run_polling()


if __name__ == "__main__":
    main()
