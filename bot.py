import os
from telegram.ext import Updater, CommandHandler

# قراءة التوكن من Secrets
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Telegram bot token is missing! تأكد من إضافة التوكن في الإعدادات.")

# مثال أمر بسيط
def start(update, context):
    update.message.reply_text("Hello! The bot is now running successfully 🎉")

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# إضافة أمر /start
dispatcher.add_handler(CommandHandler("start", start))

# تشغيل البوت
updater.start_polling()
updater.idle()
