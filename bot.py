import os
import time
import threading
import logging
from typing import Dict, Optional

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === الإعدادات من المتغيرات السرّية ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOLD_API_KEY = os.environ.get("GOLD_API_KEY")  # من GoldAPI.io
GOLD_ENDPOINT = "https://www.goldapi.io/api/XAU/USD"

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN env var")
if not GOLD_API_KEY:
    raise RuntimeError("Missing GOLD_API_KEY env var")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("gold-bot")

user_thresholds: Dict[int, float] = {}

def fetch_gold_price() -> Optional[float]:
    """يجلب سعر الأونصة بالدولار من GoldAPI"""
    try:
        headers = {
            "x-access-token": GOLD_API_KEY,
            "Content-Type": "application/json",
        }
        r = requests.get(GOLD_ENDPOINT, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        return float(data.get("price")) if data.get("price") else None
    except Exception as e:
        log.warning("fetch_gold_price error: %s", e)
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "أهلاً بك 👋\n"
        "أنا بوت تنبيهات الذهب.\n\n"
        "/price — عرض السعر الحالي\n"
        "/alert 2350 — تعيين تنبيه عند 2350$ للأونصة\n"
        "/off — إلغاء التنبيه\n"
    )
    await update.message.reply_text(text)

async def price_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = fetch_gold_price()
    if p is None:
        await update.message.reply_text("تعذّر جلب السعر الآن.")
    else:
        await update.message.reply_text(f"سعر الذهب الآن: {p:.2f} $ للأونصة.")

async def alert_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("اكتب: /alert 2350 مثلًا.")
        return
    try:
        th = float(context.args[0])
    except ValueError:
        await update.message.reply_text("القيمة غير صحيحة.")
        return

    user_id = update.effective_user.id
    user_thresholds[user_id] = th
    await update.message.reply_text(
        f"تم ضبط التنبيه عند {th:.2f}$. سأخبرك عند الوصول."
    )

async def off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_thresholds:
        del user_thresholds[user_id]
        await update.message.reply_text("تم إلغاء التنبيه.")
    else:
        await update.message.reply_text("لا يوجد تنبيه مضبوط.")

def alerts_loop(app: Application):
    while True:
        try:
            if not user_thresholds:
                time.sleep(60)
                continue

            price = fetch_gold_price()
            if price is None:
                time.sleep(60)
                continue

            to_remove = []
            for user_id, th in list(user_thresholds.items()):
                if price >= th:
                    text = (
                        f"تنبيه الذهب ⏰\n"
                        f"السعر الحالي: {price:.2f}$ للأونصة\n"
                        f"عتبتك: {th:.2f}$"
                    )
                    try:
                        app.bot.send_message(chat_id=user_id, text=text)
                        to_remove.append(user_id)
                    except Exception as e:
                        log.warning("send_message error: %s", e)

            for uid in to_remove:
                user_thresholds.pop(uid, None)

            time.sleep(60)
        except Exception as e:
            log.error("alerts_loop error: %s", e)
            time.sleep(60)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("alert", alert_cmd))
    app.add_handler(CommandHandler("off", off_cmd))

    t = threading.Thread(target=alerts_loop, args=(app,), daemon=True)
    t.start()
    log.info("Gold alert bot is running…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
