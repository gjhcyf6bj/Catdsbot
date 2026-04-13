import re
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------- কনফিগারেশন ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Render-এ BOT_TOKEN সেট করতে হবে
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

# কার্ড ফরম্যাট চেনার রেজেক্স (16 ডিজিট, তারপর বিভাজক : / বা স্পেস, 2 ডিজিট, বিভাজক, 2 ডিজিট, বিভাজক, 3 ডিজিট)
CARD_REGEX = re.compile(r'^\d{16}([:/ ])\d{2}([:/ ])\d{2}([:/ ])\d{3}$')

# ---------- টেলিগ্রাম হ্যান্ডলার ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start কমান্ডের রিপ্লাই - প্রমোশনাল মেসেজ"""
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
    """সব মেসেজ হ্যান্ডেল করে (শুধু /start ছাড়া)"""
    msg = update.message.text.strip() if update.message.text else ""

    # যদি মেসেজটি কার্ড নম্বরের ফরম্যাটে হয়
    if CARD_REGEX.match(msg):
        await update.message.reply_text(
            "You can't check the card because you're not a member of @vanilla_cards_bot"
        )
        return

    # অন্যথায় স্বাগতম মেসেজ + Buy card বাটন
    welcome = (
        "Welcome! Please provide your card details in a standard format:\n\n"
        "• 2222222222222222:22:22:222\n"
        "• 3333333333333333:33/33:333\n"
        "• 4444444444444444/44/44/444\n"
        "• 5555555555555555 55/55 555\n"
        "• 6666666666666666 66 66 666\n\n"
        "You can check your card if you're a bot member."
    )
    # বাটন তৈরি (ক্লিক করলে @vanila_card_bot-এ যাবে)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Buy card", url="https://t.me/vanila_card_bot")]
    ])
    await update.message.reply_text(welcome, reply_markup=keyboard)

# ---------- Flask অ্যাপ (হেলথ চেকের জন্য Render-এ) ----------
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is running", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

# ---------- মেইন ফাংশন ----------
def main():
    # টেলিগ্রাম অ্যাপ্লিকেশন তৈরি
    application = Application.builder().token(BOT_TOKEN).build()

    # হ্যান্ডলার যোগ
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.Regex(r'^/start(@\w+)?$'),  # শুধু /start বাদে সব টেক্সট মেসেজ
            handle_other_messages
        )
    )

    # Flask হেলথ চেক আলাদা থ্রেডে চালান (Render-এ সক্রিয় রাখতে)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # বট চালু করুন (লং পোলিং)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
