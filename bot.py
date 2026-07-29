from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8709516364:AAHKhqPEYqw7lZQWS-aaxni4dLpWg186DDM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام، ربات با موفقیت روی Render اجرا شد ✅")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Bot Started...")
app.run_polling()
