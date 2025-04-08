from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from parser import get_documents_for_days, get_failed_sources
import time

TOKEN = "7900129440:AAGixMJlvnjciet40CnlrYVuDHFSqOfLnrQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, Никита! Бот активен и готов присылать документы 🚗")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает!")

async def send_docs(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int):
    status_msg = await update.message.reply_text("🟡 Ищу документы...")
    start_time = time.time()

    docs = get_documents_for_days(days)
    elapsed_time = time.time() - start_time
    elapsed_str = f"{elapsed_time:.1f} сек"

    failed = get_failed_sources()
    if failed:
        fail_msg = "⚠️ Не удалось подключиться к:\n" + "\n".join(f"- {src}" for src in failed)
        await update.message.reply_text(fail_msg)

    if not docs:
        await status_msg.edit_text(f"⚠️ Документы не найдены. Обработка заняла {elapsed_str}.")
        return

    await status_msg.edit_text(f"✅ Найдено {len(docs)} документов за {elapsed_str}. Отправляю:")

    for doc in docs:
        msg = (
            f"📅 {doc['date']}\n"
            f"📝 {doc['title']}\n"
            f"🌐 Источник: {doc['source']}\n"
            f"🏷️ Темы: {', '.join(doc['topics'])}\n"
            f"🔗 {doc['url']}"
        )
        await update.message.reply_text(msg)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_docs(update, context, 0)

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_docs(update, context, 7)

async def twoweeks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_docs(update, context, 14)

async def month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_docs(update, context, 30)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("test", test))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("week", week))
app.add_handler(CommandHandler("twoweeks", twoweeks))
app.add_handler(CommandHandler("month", month))

print("🚀 Бот запущен и ждёт команды...")
app.run_polling()
