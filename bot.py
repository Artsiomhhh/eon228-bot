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

FREE_IMAGES = [
    "marin_01.png",
    "marin_02.png",
    "marin_03.png",
    "marin_04.png",
    "marin_05.png",
]

CUSTOM_IMAGE_STARS = 750


bot.set_my_commands([
    types.BotCommand("start", "Open main menu"),
    types.BotCommand("free", "Get FREE Marin Kitagawa Pack"),
    types.BotCommand("about", "About EgoEON AI"),
    types.BotCommand("stats", "Bot statistics")
])


def default_stats():
    return {
        "starts": 0,
        "free_clicks": 0,
        "free_downloads": 0
    }


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
        return default_stats(), None

    r.raise_for_status()
    data = r.json()
    content = base64.b64decode(data["content"]).decode("utf-8")

    try:
        stats = json.loads(content)
    except Exception:
        stats = default_stats()

    for key, value in default_stats().items():
        if key not in stats:
            stats[key] = value

    return stats, data["sha"]


def save_stats(stats, sha=None):
    content = base64.b64encode(
        json.dumps(stats, indent=2).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": "Update bot stats",
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


def update_stat(key):
    stats, sha = load_stats()
    stats[key] = stats.get(key, 0) + 1
    save_stats(stats, sha)
    return stats


def get_stats():
    stats, _ = load_stats()
    return stats


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(
            "🎁 Download FREE Marin Kitagawa Pack",
            callback_data="free_pack"
        )
    )

    markup.row(
        types.InlineKeyboardButton("💖 Nami Pack", callback_data="nami"),
        types.InlineKeyboardButton("❤️ Yor Pack", callback_data="yor")
    )

    markup.row(
        types.InlineKeyboardButton("💙 Android 18 Pack", callback_data="android18"),
        types.InlineKeyboardButton("🔥 All Packs Bundle", callback_data="bundle")
    )

    markup.add(
        types.InlineKeyboardButton("🎨 Custom Image — $15", callback_data="custom"),
        types.InlineKeyboardButton("ℹ️ About", callback_data="about")
    )

    return markup


def send_main_menu(chat_id):
    try:
        stats = update_stat("starts")
    except Exception:
        stats = default_stats()

    bot.send_message(
        chat_id,
        "🔥 Welcome to EgoEON AI Store\n\n"
        "🎁 FREE Marin Kitagawa Pack\n"
        "✅ 5 HD anime wallpapers\n"
        "📱 Phone optimized\n"
        "✨ AI generated\n\n"
        f"🔥 Claimed by: {stats.get('free_downloads', 0)} people\n\n"
        "Tap the button below to download instantly 👇",
        reply_markup=main_menu()
    )


def send_free_pack(chat_id, user):
    username = user.username or "no_username"

    try:
        update_stat("free_clicks")
    except Exception:
        pass

    if os.path.exists(PREVIEW_PATH):
        with open(PREVIEW_PATH, "rb") as photo:
            bot.send_photo(
                chat_id,
                photo,
                caption=(
                    "🎁 FREE Marin Kitagawa Pack\n\n"
                    "Includes 5 HD wallpapers 📱\n\n"
                    "✨ AI generated\n"
                    "💖 Mobile optimized\n\n"
                    "Sending wallpapers below 👇"
                )
            )

    if not all(os.path.exists(path) for path in FREE_IMAGES):
        bot.send_message(chat_id, "❌ One or more Marin image files are missing.")
        return

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
        stats = update_stat("free_downloads")
        downloads = stats.get("free_downloads", 0)
    except Exception:
        downloads = "unknown"

    bot.send_message(
        chat_id,
        "✅ Done! Enjoy your free wallpapers 💖\n\n"
        f"🎁 Free pack claimed: {downloads} times",
        reply_markup=main_menu()
    )

    if ADMIN_ID:
        bot.send_message(
            int(ADMIN_ID),
            "🎁 FREE Marin Kitagawa Pack downloaded\n\n"
            f"User: @{username}\n"
            f"User ID: {chat_id}\n"
            f"Total downloads: {downloads}"
        )


@bot.message_handler(commands=["start"])
def start(message):
    send_main_menu(message.chat.id)


@bot.message_handler(commands=["free"])
def free_command(message):
    send_free_pack(message.chat.id, message.from_user)


@bot.message_handler(commands=["about"])
def about_command(message):
    bot.send_message(
        message.chat.id,
        "EgoEON AI creates anime wallpaper packs.\n\n"
        "✨ HD quality\n"
        "📱 Mobile optimized\n"
        "🎨 AI anime artwork\n"
        "🎁 Free and premium packs\n\n"
        "New packs are added regularly.",
        reply_markup=main_menu()
    )


@bot.message_handler(commands=["stats"])
def stats_command(message):
    if not ADMIN_ID or str(message.chat.id) != str(ADMIN_ID):
        bot.send_message(message.chat.id, "❌ Admin only.")
        return

    try:
        stats = get_stats()
        bot.send_message(
            message.chat.id,
            "📊 Bot Stats\n\n"
            f"Starts: {stats.get('starts', 0)}\n"
            f"Free pack clicks: {stats.get('free_clicks', 0)}\n"
            f"Free downloads: {stats.get('free_downloads', 0)}"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"Stats error: {e}")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    if call.data == "free_pack":
        bot.answer_callback_query(call.id)
        send_free_pack(chat_id, call.from_user)

    elif call.data == "nami":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "💖 Nami Pack — $3\n\nPayment system coming soon.")

    elif call.data == "yor":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "❤️ Yor Pack — $3\n\nPayment system coming soon.")

    elif call.data == "android18":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "💙 Android 18 Pack — $3\n\nPayment system coming soon.")

    elif call.data == "bundle":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🔥 All Packs Bundle — $7\n\nPayment system coming soon.")

    elif call.data == "about":
        bot.answer_callback_query(call.id)
        about_command(call.message)

    elif call.data == "custom":
        bot.answer_callback_query(call.id)
        bot.send_invoice(
            chat_id=chat_id,
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
            bot.send_message(
                int(ADMIN_ID),
                "💰 New paid Custom Image order!\n\n"
                f"User: @{message.from_user.username or 'no_username'}\n"
                f"User ID: {message.chat.id}\n"
                f"Stars paid: {payment.total_amount}"
            )


@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(
        message.chat.id,
        "Use the menu below 👇",
        reply_markup=main_menu()
    )


print("Bot started - inline menu version")
bot.remove_webhook()
bot.infinity_polling(skip_pending=True)
