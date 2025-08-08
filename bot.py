import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# جلب التوكن من Environment Variables أو Secrets
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8320369580:AAH1cOKkitU2jYQxG2NbpDbGmbq3h64TtqM")

# دالة الرد على أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Hello! Gold Price Bot is working.")

# إنشاء التطبيق وتشغيله
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
