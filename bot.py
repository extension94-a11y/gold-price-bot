import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN")

# أنشئ عميل httpx مع تعطيل أي بروكسي من البيئة
httpx_client = httpx.Client(trust_env=False, timeout=30.0)

# مرّره إلى HTTPXRequest
request = HTTPXRequest(httpx_client=httpx_client)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت شغّال. اكتب /ping")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong 🏓")

def main():
    app = Application.builder().token(TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
