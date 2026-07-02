import os
import json
import base64
import requests
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is not set")
if not GITHUB_REPO:
    raise RuntimeError("GITHUB_REPO is not set")

bot = telebot.TeleBot(TOKEN)

PREVIEW_PATH = "marin_preview.png"
STATS_PATH = "stats.json"
CUSTOM_IMAGE_STARS = 750

FREE_IMAGES = [
    "marin_01.png",
    "marin_02.png",
    "marin_03.png",
    "marin_04.png",
    "marin_05.png",
]


def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }


def github_file_url(path):
    return f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"


def load_stats():
    r = requests.get(
        github_file_url(STATS_PATH),
        headers=github_headers(),
        params={"ref": GITHUB_BRANCH}
    )

    if r.status_code == 404:
        return {"free_downloads": 0}, None

    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return json.loads(content), data["sha"]


def save_stats(stats, sha=None):
    content = base64.b64encode(
        json.dumps(stats, indent=2).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": "Update stats",
        "content": content,
        "branch": GITHUB_BRANCH
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(
        github_file_url(STATS_PATH),
        headers=github_headers(),
        json=payload
    )
    r.raise_for_status()


def get_free_downloads():
    stats, _ = load_stats()
    return stats.get("free_downloads", 0)


def increment_free_downloads():
    stats, sha = load_stats()
    stats["free_downloads"] = stats.get("free_downloads", 0) + 1
    save_stats(stats, sha)
    return stats["free_downloads"]


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 FREE Marin Kitagawa Pack")
    markup.add("💖 Nami Pack", "❤️ Yor Pack")
    markup.add("💙 Android 18 Pack", "🔥 All Packs Bundle")
    markup.add("🎨 Custom Image — $15")
    markup.add("ℹ️ About")
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    try:
        downloads = get_free_downloads()
    except Exception:
        downloads = 0

    bot.send_message(
        message.chat.id,
        "🔥 Welcome to EgoEON AI Store\n\n"
        "Download exclusive AI anime wallpaper packs:\n\n"
        f"🎁 FREE Marin Kitagawa Pack downloads: {downloads}\n"
        "✅ Includes 5 HD wallpapers\n\n"
        "💖 Nami Pack\n"
        "❤️ Yor Pack\n"
        "💙 Android 18 Pack\n"
        "🔥 Bundle Pack\n"
        "🎨 Custom Image — $15\n\n"
        "📱 All wallpapers are optimized for mobile devices.\n\n"
        "Choose a pack below 👇",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: message.text == "🎨 Custom Image — $15")
def custom_image(message):
    bot.send_invoice(
        chat_id=message.chat.id,
        title="Custom Anime Image",
        description="1 custom AI anime-style image. Send your idea after payment.",
        invoice_payload="custom_image_15",
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label="Custom Image", amount=CUSTOM_IMAGE_STARS)]
    )


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=["successful_payment"])
def got_payment(message):
    payment = message.successful_payment

    if payment.invoice_payload == "custom_image_15":
        bot.send_message(
            message.chat.id,
            "✅ Payment received!\n\n"
            "Now send your custom image request in one message:\n\n"
            "1. Character idea or reference\n"
            "2. Outfit/style\n"
            "3. Pose or mood\n"
            "4. Wallpaper size if needed"
        )

        if ADMIN_ID:
            username = message.from_user.username
            bot.send_message(
                int(ADMIN_ID),
                "💰 New paid Custom Image order!\n\n"
                f"User: @{username if username else 'no_username'}\n"
                f"User ID: {message.chat.id}\n"
                f"Stars paid: {payment.total_amount}\n"
                f"Charge ID: {payment.telegram_payment_charge_id}"
            )


@bot.message_handler(content_types=["text"], func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    username = message.from_user.username

    if text == "🎁 FREE Marin Kitagawa Pack":
        if os.path.exists(PREVIEW_PATH):
            with open(PREVIEW_PATH, "rb") as photo:
                bot.send_photo(
                    chat_id,
                    photo,
                    caption=(
                        "🎁 FREE Marin Kitagawa Pack\n\n"
                        "Includes 5 exclusive HD wallpapers 📱\n\n"
                        "✨ AI generated\n"
                        "💖 Mobile optimized\n\n"
                        "Sending wallpapers below 👇"
                    )
                )

        if all(os.path.exists(path) for path in FREE_IMAGES):
            files = []
            media = []

            try:
                for path in FREE_IMAGES:
                    f = open(path, "rb")
                    files.append(f)
                    media.append(types.InputMediaPhoto(f))

                bot.send_media_group(chat_id, media)

            finally:
                for f in files:
                    f.close()

            try:
                new_count = increment_free_downloads()
            except Exception as e:
                new_count = "unknown"
                bot.send_message(chat_id, f"⚠️ Stats error: {e}")

            bot.send_message(
                chat_id,
                "✅ Done! Enjoy your free wallpapers 💖\n\n"
                f"Total free pack downloads: {new_count}"
            )

            if ADMIN_ID:
                bot.send_message(
                    int(ADMIN_ID),
                    "🎁 FREE Marin Kitagawa Pack downloaded\n\n"
                    f"User: @{username if username else 'no_username'}\n"
                    f"User ID: {chat_id}\n"
                    f"Total downloads: {new_count}"
                )
        else:
            bot.send_message(
                chat_id,
                "❌ One or more Marin wallpaper files are missing."
            )

    elif text == "💖 Nami Pack":
        bot.send_message(chat_id, "💖 Nami Pack — $3\n\nPayment system coming soon.")

    elif text == "❤️ Yor Pack":
        bot.send_message(chat_id, "❤️ Yor Pack — $3\n\nPayment system coming soon.")

    elif text == "💙 Android 18 Pack":
        bot.send_message(chat_id, "💙 Android 18 Pack — $3\n\nPayment system coming soon.")

    elif text == "🔥 All Packs Bundle":
        bot.send_message(chat_id, "🔥 All Packs Bundle — $7\n\nPayment system coming soon.")

    elif text == "ℹ️ About":
        bot.send_message(
            chat_id,
            "EgoEON AI creates anime wallpaper packs.\n\n"
            "✨ HD quality\n"
            "📱 Mobile optimized\n"
            "🎨 AI anime artwork\n"
            "🎁 Free and premium packs\n\n"
            "New packs are added regularly."
        )

    else:
        bot.send_message(chat_id, "Choose a pack from the menu 👇", reply_markup=main_menu())


print("Bot started - Marin album version")
bot.remove_webhook()
bot.infinity_polling(skip_pending=True)
