import re
import os
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- কনফিগারেশন ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

CARD_REGEX = re.compile(r'^\d{16}([:/ ])\d{2}([:/ ])\d{2}([:/ ])\d{3}$')

# ---------- টেলিগ্রাম হ্যান্ডলার ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💠 Dear users!\n\n"
        "🚀 JOIN OUR OFFICIAL BOT FIRST!\n"
        "🤖 Buy Cards Instantly:\n"
        "👉 <a href='https://t.me/vanilla_cards_bot'>@vanilla_cards_bot</a> — Type /start\n"
        "🔔 Get Instant Support: <a href='https://t.me/Vanila_card_prepaid'>https://t.me/Vanila_card_prepaid</a>\n"
        "⚡ Early Join = Early Access\n"
        "🔥 Don’t Miss The Best Cards !"
    )
    await update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip() if update.message.text else ""
    if CARD_REGEX.match(msg):
        await update.message.reply_text(
            "You can't check the card because you're not a member of @vanilla_cards_bot"
        )
        return

    welcome = (
        "Welcome! Please provide your card details in a standard format:\n\n"
        "• 2222222222222222:22:22:222\n"
        "• 3333333333333333:33/33:333\n"
        "• 4444444444444444/44/44/444\n"
        "• 5555555555555555 55/55 555\n"
        "• 6666666666666666 66 66 666\n\n"
        "You can check your card if you're a bot member."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Buy card", url="https://t.me/vanila_card_bot")]
    ])
    await update.message.reply_text(welcome, reply_markup=keyboard)

# ---------- Flask অ্যাপ (হেলথ চেক) ----------
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is running", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# ---------- মেইন ফাংশন (অ্যাসিন্ক) ----------
async def main():
    # ইভেন্ট লুপ ঠিক করার জন্য (Python 3.14 এ প্রয়োজন)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.Regex(r'^/start(@\w+)?$'),
            handle_other_messages
        )
    )

    # Flask হেলথ চেক আলাদা থ্রেডে চালান
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # বট চালু (লং পোলিং)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    # বট চালু থাকার জন্য সিগন্যাল ওয়েট
    stop_signal = asyncio.Event()
    await stop_signal.wait()

# ---------- এন্ট্রি পয়েন্ট ----------
if __name__ == "__main__":
    # পাইথন ৩.১৪ এর জন্য নতুন ইভেন্ট লুপ নীতি
    asyncio.run(main())
