import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import BOT_TOKEN
from utils.aggregator import get_all_completed
from utils.volumes import split_into_volumes
from utils.cbz import create_volume_cbz


async def finalizados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mangas, manhwas = await get_all_completed()

    context.chat_data["mangas"] = mangas
    context.chat_data["manhwas"] = manhwas

    text = f"""
📚 Mangás finalizados: {len(mangas)}
📖 Manhwas finalizados: {len(manhwas)}
Total: {len(mangas) + len(manhwas)}
"""

    buttons = [
        [InlineKeyboardButton("📥 Baixar Mangás", callback_data="download_manga")],
        [InlineKeyboardButton("📥 Baixar Manhwas", callback_data="download_manhwa")]
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


async def download_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "download_manga":
        items = context.chat_data.get("mangas", [])
    else:
        items = context.chat_data.get("manhwas", [])

    for manga in items:
        await process_manga(query.message, manga)


async def process_manga(message, manga):
    title = manga["title"]
    cover = manga["cover"]
    chapters = manga["chapters"]
    source = manga["source"]

    volumes = split_into_volumes(chapters, 50)

    await message.reply_photo(
        photo=cover,
        caption=f"""
📖 {title}
📌 Status: Finalizado
📊 Capítulos: {len(chapters)}
📦 Volumes: {len(volumes)}
"""
    )

    for i, volume in enumerate(volumes, start=1):
        cbz_path, cbz_name = await create_volume_cbz(
            source, volume, title, i
        )

        await message.reply_document(
            document=open(cbz_path, "rb"),
            filename=cbz_name
        )

        os.remove(cbz_path)
        await asyncio.sleep(0.5)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("finalizados", finalizados))
    app.add_handler(CallbackQueryHandler(download_type, pattern="^download_"))

    app.run_polling()


if __name__ == "__main__":
    main()
