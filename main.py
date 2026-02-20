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
from utils.aggregator import get_completed_by_genre
from utils.volumes import split_into_volumes
from utils.cbz import create_volume_cbz


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Bot Online\n\n"
        "Use:\n"
        "/bb3 romance"
    )


async def bb3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Use:\n/bb3 genero")

    genre = " ".join(context.args)

    msg = await update.message.reply_text("🔎 Buscando...")

    mangas, manhwas = await get_completed_by_genre(genre)

    if not mangas and not manhwas:
        return await msg.edit_text("❌ Nenhum finalizado encontrado.")

    context.chat_data["mangas"] = mangas
    context.chat_data["manhwas"] = manhwas

    text = (
        f"📖 Gênero: {genre}\n\n"
        f"📚 Mangás finalizados: {len(mangas)}\n"
        f"📘 Manhwas finalizados: {len(manhwas)}"
    )

    buttons = [
        [InlineKeyboardButton("📥 Baixar Mangás", callback_data="download_manga")],
        [InlineKeyboardButton("📥 Baixar Manhwas", callback_data="download_manhwa")]
    ]

    await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


async def download_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_manga":
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
    manga_type = manga["type"]

    if not chapters:
        return

    volumes = split_into_volumes(chapters, 50)

    if cover:
        await message.reply_photo(
            photo=cover,
            caption=(
                f"📖 {title}\n"
                f"📚 Tipo: {manga_type}\n"
                f"📌 Status: Finalizado\n"
                f"📊 Capítulos: {len(chapters)}\n"
                f"📦 Volumes: {len(volumes)}"
            )
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

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bb3", bb3))
    app.add_handler(CallbackQueryHandler(download_type, pattern="^download_"))

    print("BOT INICIADO")

    app.run_polling()


if __name__ == "__main__":
    main()
