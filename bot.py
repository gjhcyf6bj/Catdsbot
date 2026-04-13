import re
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- কনফিগারেশন ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

# কার্ড ফরম্যাট চেনার রেজেক্স
CARD_REGEX = re.compile(r'^\d{16}([:/ ])\d{2}([:/ ])\d{2}([:/ ])\d{3}$')

# ক্লিক করে কপি করার জন্য বাটনের ফরম্যাট লিস্ট
CARD_FORMATS = [
    "2222222222222222:22:22:222",
    "3333333333333333:33/33:333",
    "4444444444444444/44/44/444",
    "5555555555555555 55/55 555",
    "6666666666666666 66 66 666"
]

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
        "Click the buttons below to copy each format."
    )
    keyboard = [
        [InlineKeyboardButton(text=f"Copy {i+1}", copy_text=fmt)]
        for i, fmt in enumerate(CARD_FORMATS)
    ]
    await update.message.reply_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard))

# ---------- Flask অ্যাপ (শুধু হেলথ চেকের জন্য) ----------
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is running", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# ---------- মেইন ফাংশন ----------
def main():
    # টেলিগ্রাম বট চালু করি
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.Regex(r'^/(start|help)(@\w+)?$'), handle_other_messages)
    )

    # Flask হেলথ চেক সার্ভার আলাদা থ্রেডে চালাই
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # বট লং পোলিং শুরু
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
