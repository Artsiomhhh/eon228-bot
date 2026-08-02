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
BOA_CHANNEL_ID = os.getenv("BOA_CHANNEL_ID")
BOA_MESSAGE_ID = os.getenv("BOA_MESSAGE_ID")
NAMI_CHANNEL_ID = os.getenv("NAMI_CHANNEL_ID")
NAMI_MESSAGE_ID = os.getenv("NAMI_MESSAGE_ID")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is not set")
if not GITHUB_REPO:
    raise RuntimeError("GITHUB_REPO is not set")

bot = telebot.TeleBot(TOKEN)

MARIN_PREVIEW_PATH = "marin_preview.png"
STATS_PATH = "stats.json"

FREE_IMAGES = [
    "marin_01.png",
    "marin_02.png",
    "marin_03.png",
    "marin_04.png",
    "marin_05.png",
]

BOA_PREVIEWS = [
    "boa_preview_01.png",
    "boa_preview_02.png",
    "boa_preview_03.png",
]

NAMI_PREVIEWS = [
    "nami_preview_01.png",
    "nami_preview_02.png",
    "nami_preview_03.png",
]

BOA_PACK_STARS = 99
NAMI_PACK_STARS = 99
CUSTOM_IMAGE_STARS = 750


def is_admin(chat_id):
    return bool(ADMIN_ID) and str(chat_id) == str(ADMIN_ID)


def get_boa_source():
    if not BOA_CHANNEL_ID or not BOA_MESSAGE_ID:
        return None, None
    try:
        return int(BOA_CHANNEL_ID), int(BOA_MESSAGE_ID)
    except ValueError:
        return None, None


def get_nami_source():
    if not NAMI_CHANNEL_ID or not NAMI_MESSAGE_ID:
        return None, None
    try:
        return int(NAMI_CHANNEL_ID), int(NAMI_MESSAGE_ID)
    except ValueError:
        return None, None


def default_stats():
    return {
        "starts": 0,
        "free_clicks": 0,
        "free_delivered": 0,
        "nami_clicks": 0,
        "nami_sales": 0,
        "nami_delivered": 0,
        "boa_clicks": 0,
        "boa_sales": 0,
        "boa_delivered": 0,
    }


def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def github_file_url(path):
    return f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"


def load_stats():
    response = requests.get(
        github_file_url(STATS_PATH),
        headers=github_headers(),
        params={"ref": GITHUB_BRANCH},
        timeout=20,
    )
    if response.status_code == 404:
        return default_stats(), None
    response.raise_for_status()
    data = response.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    try:
        stats = json.loads(content)
    except Exception:
        stats = default_stats()
    if "free_downloads" in stats and "free_delivered" not in stats:
        stats["free_delivered"] = stats.get("free_downloads", 0)
    stats.pop("free_downloads", None)
    for key, value in default_stats().items():
        stats.setdefault(key, value)
    return stats, data["sha"]


def save_stats(stats, sha=None):
    content = base64.b64encode(
        json.dumps(stats, indent=2).encode("utf-8")
    ).decode("utf-8")
    payload = {
        "message": "Update bot stats",
        "content": content,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha
    response = requests.put(
        github_file_url(STATS_PATH),
        headers=github_headers(),
        json=payload,
        timeout=20,
    )
    response.raise_for_status()


def update_stat(key):
    stats, sha = load_stats()
    stats[key] = stats.get(key, 0) + 1
    save_stats(stats, sha)
    return stats


def get_stats():
    stats, _ = load_stats()
    return stats


def register_commands():
    bot.set_my_commands([
        types.BotCommand("start", "Open main menu"),
        types.BotCommand("free", "Get FREE Starter Pack"),
        types.BotCommand("nami", "Open Nami Premium Pack"),
        types.BotCommand("boa", "Open Boa Hancock Premium Pack"),
        types.BotCommand("about", "About EgoEON AI"),
        types.BotCommand("stats", "Bot statistics"),
    ])


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)

    markup.add(
        types.InlineKeyboardButton(
            "🎁 FREE Starter Pack",
            callback_data="free_pack",
        )
    )

    markup.row(
        types.InlineKeyboardButton(
            "💖 Nami Premium Pack — 99 ⭐",
            callback_data="nami",
        ),
        types.InlineKeyboardButton(
            "👑 Boa Hancock Premium Pack — 99 ⭐",
            callback_data="boa",
        ),
    )

    markup.add(
        types.InlineKeyboardButton(
            "❤️ Yor Premium Pack — Coming Soon",
            callback_data="yor",
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔥 All Packs Bundle — Coming Soon",
            callback_data="bundle",
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🎨 Custom Image — 750 ⭐",
            callback_data="custom",
        ),
        types.InlineKeyboardButton(
            "ℹ️ About",
            callback_data="about",
        ),
    )

    return markup

def remove_old_keyboard(chat_id):
    bot.send_message(chat_id, "Menu updated ✅", reply_markup=types.ReplyKeyboardRemove())


def send_main_menu(chat_id, remove_keyboard=True):
    try:
        stats = update_stat("starts")
    except Exception:
        stats = default_stats()
    if remove_keyboard:
        remove_old_keyboard(chat_id)
    bot.send_message(
        chat_id,
        "🔥 EgoEON AI Store\n\n"
        "🎁 FREE Starter Pack\n"
        "(5 HD Wallpapers)\n\n"
        "⭐ Premium Packs\n\n"
        "💖 Nami\n"
        "👑 Boa Hancock\n"
        "❤️ Yor\n\n"
        "👇 Choose your favorite character",
        reply_markup=main_menu(),
    )


def send_free_pack(chat_id, user):
    username = user.username or "no_username"
    try:
        update_stat("free_clicks")
    except Exception:
        pass
    if os.path.exists(MARIN_PREVIEW_PATH):
        with open(MARIN_PREVIEW_PATH, "rb") as photo:
            bot.send_photo(
                chat_id,
                photo,
                caption=(
                    "🎁 FREE Marin Kitagawa Pack\n\n"
                    "Includes 5 HD wallpapers 📱\n\n"
                    "✨ AI generated\n"
                    "💖 Mobile optimized\n\n"
                    "Sending wallpapers below 👇"
                ),
            )
    missing = [path for path in FREE_IMAGES if not os.path.exists(path)]
    if missing:
        bot.send_message(chat_id, "❌ Missing image files:\n" + "\n".join(missing))
        return
    files, media = [], []
    try:
        for path in FREE_IMAGES:
            file = open(path, "rb")
            files.append(file)
            media.append(types.InputMediaPhoto(file))
        bot.send_media_group(chat_id, media)
    except Exception as error:
        bot.send_message(chat_id, f"❌ Could not send wallpapers: {error}")
        return
    finally:
        for file in files:
            try:
                file.close()
            except Exception:
                pass
    try:
        stats = update_stat("free_delivered")
        delivered = stats.get("free_delivered", 0)
    except Exception:
        delivered = "unknown"
    bot.send_message(
        chat_id,
        "✅ Done! Enjoy your free wallpapers 💖\n\n"
        f"🎁 Free pack delivered: {delivered} times",
        reply_markup=main_menu(),
    )
    if ADMIN_ID:
        try:
            bot.send_message(
                int(ADMIN_ID),
                "🎁 FREE Marin Kitagawa Pack delivered\n\n"
                f"User: @{username}\n"
                f"User ID: {chat_id}\n"
                f"Total delivered: {delivered}",
            )
        except Exception:
            pass


def send_nami_previews(chat_id):
    try:
        update_stat("nami_clicks")
    except Exception:
        pass

    missing = [path for path in NAMI_PREVIEWS if not os.path.exists(path)]
    if missing:
        bot.send_message(
            chat_id,
            "❌ Nami previews are temporarily unavailable.\n\nMissing:\n"
            + "\n".join(missing),
        )
        if ADMIN_ID:
            try:
                bot.send_message(
                    int(ADMIN_ID),
                    "⚠️ Missing Nami preview files:\n" + "\n".join(missing),
                )
            except Exception:
                pass
        return

    files, media = [], []
    try:
        for index, path in enumerate(NAMI_PREVIEWS):
            file = open(path, "rb")
            files.append(file)
            caption = None
            if index == 0:
                caption = (
                    "💖 Nami Premium Pack\n\n"
                    "✨ 20 HD anime wallpapers\n"
                    "📱 Perfect for phones\n"
                    "💻 Easy download on PC\n"
                    "📦 Delivered as one ZIP archive\n"
                    "🚫 No watermarks\n\n"
                    "⭐ Price: 99 Stars"
                )
            media.append(types.InputMediaPhoto(media=file, caption=caption))

        bot.send_media_group(chat_id, media)

    except Exception as error:
        bot.send_message(chat_id, f"❌ Could not send Nami previews: {error}")
        return

    finally:
        for file in files:
            try:
                file.close()
            except Exception:
                pass

    bot.send_invoice(
        chat_id=chat_id,
        title="Nami Wallpaper Pack",
        description=(
            "20 HD Nami wallpapers delivered as one ZIP archive. "
            "Downloadable on phone and PC."
        ),
        invoice_payload="nami_pack_99",
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label="Nami Pack", amount=NAMI_PACK_STARS)],
    )


def send_boa_previews(chat_id):
    try:
        update_stat("boa_clicks")
    except Exception:
        pass
    missing = [path for path in BOA_PREVIEWS if not os.path.exists(path)]
    if missing:
        bot.send_message(
            chat_id,
            "❌ Boa Hancock previews are temporarily unavailable.\n\nMissing:\n"
            + "\n".join(missing),
        )
        if ADMIN_ID:
            try:
                bot.send_message(int(ADMIN_ID), "⚠️ Missing Boa preview files:\n" + "\n".join(missing))
            except Exception:
                pass
        return
    files, media = [], []
    try:
        for index, path in enumerate(BOA_PREVIEWS):
            file = open(path, "rb")
            files.append(file)
            caption = None
            if index == 0:
                caption = (
                    "👑 Boa Hancock Premium Pack\n\n"
                    "✨ 20 HD anime wallpapers\n"
                    "📱 Perfect for phones\n"
                    "💻 Easy download on PC\n"
                    "📦 Delivered as one ZIP archive\n"
                    "🚫 No watermarks\n\n"
                    "⭐ Price: 99 Stars"
                )
            media.append(types.InputMediaPhoto(media=file, caption=caption))
        bot.send_media_group(chat_id, media)
    except Exception as error:
        bot.send_message(chat_id, f"❌ Could not send Boa previews: {error}")
        return
    finally:
        for file in files:
            try:
                file.close()
            except Exception:
                pass
    bot.send_invoice(
        chat_id=chat_id,
        title="Boa Hancock Wallpaper Pack",
        description=(
            "20 HD Boa Hancock wallpapers delivered as one ZIP archive. "
            "Downloadable on phone and PC."
        ),
        invoice_payload="boa_hancock_pack_99",
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label="Boa Hancock Pack", amount=BOA_PACK_STARS)],
    )


def deliver_nami_pack(message):
    channel_id, message_id = get_nami_source()

    if channel_id is None or message_id is None:
        bot.send_message(
            message.chat.id,
            "⚠️ Payment received, but the Nami pack is temporarily unavailable.\n"
            "Support has been notified.",
        )
        if ADMIN_ID:
            try:
                bot.send_message(
                    int(ADMIN_ID),
                    "🚨 Nami payment received, but NAMI_CHANNEL_ID or "
                    "NAMI_MESSAGE_ID is not configured.\n\n"
                    f"Buyer ID: {message.chat.id}",
                )
            except Exception:
                pass
        return False

    try:
        bot.send_message(
            message.chat.id,
            "✅ Payment received!\n\nYour Nami pack is ready 👇",
        )

        bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=channel_id,
            message_id=message_id,
        )

        try:
            stats = update_stat("nami_delivered")
            total_delivered = stats.get("nami_delivered", 0)
        except Exception:
            total_delivered = "unknown"

        bot.send_message(
            message.chat.id,
            "✅ Nami Premium Pack delivered!\n\n"
            "📱 On phone: tap the ZIP file and download it.\n"
            "💻 On PC: click the download icon and extract the archive.\n\n"
            "Thank you for your purchase 💖",
            reply_markup=main_menu(),
        )

        if ADMIN_ID:
            try:
                bot.send_message(
                    int(ADMIN_ID),
                    "💰 Nami Premium Pack sold!\n\n"
                    f"User: @{message.from_user.username or 'no_username'}\n"
                    f"User ID: {message.chat.id}\n"
                    f"Stars paid: {message.successful_payment.total_amount}\n"
                    f"Total Nami deliveries: {total_delivered}",
                )
            except Exception:
                pass

        return True

    except Exception as error:
        bot.send_message(
            message.chat.id,
            "⚠️ Payment was received, but Telegram could not deliver the Nami ZIP.\n"
            "Support has been notified.",
        )
        if ADMIN_ID:
            try:
                bot.send_message(
                    int(ADMIN_ID),
                    "🚨 Nami Pack delivery error\n\n"
                    f"Buyer ID: {message.chat.id}\n"
                    f"Error: {error}",
                )
            except Exception:
                pass
        return False


def deliver_boa_pack(message):
    channel_id, message_id = get_boa_source()
    if channel_id is None or message_id is None:
        bot.send_message(
            message.chat.id,
            "⚠️ Payment received, but the pack is temporarily unavailable.\n"
            "Support has been notified.",
        )
        if ADMIN_ID:
            try:
                bot.send_message(
                    int(ADMIN_ID),
                    "🚨 Boa payment received, but BOA_CHANNEL_ID or BOA_MESSAGE_ID "
                    "is not configured.\n\n"
                    f"Buyer ID: {message.chat.id}",
                )
            except Exception:
                pass
        return False
    try:
        bot.send_message(message.chat.id, "✅ Payment received!\n\nYour Boa Hancock pack is ready 👇")
        bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=channel_id,
            message_id=message_id,
        )
        try:
            stats = update_stat("boa_delivered")
            total_delivered = stats.get("boa_delivered", 0)
        except Exception:
            total_delivered = "unknown"
        bot.send_message(
            message.chat.id,
            "✅ Boa Hancock Pack delivered!\n\n"
            "📱 On phone: tap the ZIP file and download it.\n"
            "💻 On PC: click the download icon and extract the archive.\n\n"
            "Thank you for your purchase 💖",
            reply_markup=main_menu(),
        )
        if ADMIN_ID:
            try:
                bot.send_message(
                    int(ADMIN_ID),
                    "💰 Boa Hancock Pack sold!\n\n"
                    f"User: @{message.from_user.username or 'no_username'}\n"
                    f"User ID: {message.chat.id}\n"
                    f"Stars paid: {message.successful_payment.total_amount}\n"
                    f"Total Boa deliveries: {total_delivered}",
                )
            except Exception:
                pass
        return True
    except Exception as error:
        bot.send_message(
            message.chat.id,
            "⚠️ Payment was received, but Telegram could not deliver the ZIP.\n"
            "Support has been notified.",
        )
        if ADMIN_ID:
            try:
                bot.send_message(
                    int(ADMIN_ID),
                    "🚨 Boa Pack delivery error\n\n"
                    f"Buyer ID: {message.chat.id}\n"
                    f"Error: {error}",
                )
            except Exception:
                pass
        return False


@bot.message_handler(commands=["start"])
def start(message):
    send_main_menu(message.chat.id, remove_keyboard=True)


@bot.message_handler(commands=["free"])
def free_command(message):
    send_free_pack(message.chat.id, message.from_user)


@bot.message_handler(commands=["nami"])
def nami_command(message):
    send_nami_previews(message.chat.id)


@bot.message_handler(commands=["boa"])
def boa_command(message):
    send_boa_previews(message.chat.id)


@bot.message_handler(commands=["about"])
def about_command(message):
    bot.send_message(
        message.chat.id,
        "🔥 EgoEON AI Store\n\n"
        "✨ HD quality\n"
        "📱 Mobile optimized\n"
        "💻 PC-friendly downloads\n"
        "🎨 AI anime artwork\n"
        "🎁 Free and premium packs\n\n"
        "New packs are added regularly.",
        reply_markup=main_menu(),
    )


@bot.message_handler(commands=["stats"])
def stats_command(message):
    if not is_admin(message.chat.id):
        bot.send_message(message.chat.id, "❌ Admin only.")
        return
    try:
        stats = get_stats()
        bot.send_message(
            message.chat.id,
            "📊 Bot Stats\n\n"
            f"Starts: {stats.get('starts', 0)}\n"
            f"FREE clicks: {stats.get('free_clicks', 0)}\n"
            f"FREE delivered: {stats.get('free_delivered', 0)}\n\n"
            f"Nami clicks: {stats.get('nami_clicks', 0)}\n"
            f"Nami sales: {stats.get('nami_sales', 0)}\n"
            f"Nami delivered: {stats.get('nami_delivered', 0)}\n\n"
            f"Boa clicks: {stats.get('boa_clicks', 0)}\n"
            f"Boa sales: {stats.get('boa_sales', 0)}\n"
            f"Boa delivered: {stats.get('boa_delivered', 0)}\n\n"
            "FREE delivered means the full free album was sent.\n"
            "Boa delivered means the paid ZIP was copied to the buyer.",
        )
    except Exception as error:
        bot.send_message(message.chat.id, f"Stats error: {error}")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "free_pack":
        bot.answer_callback_query(call.id)
        send_free_pack(chat_id, call.from_user)
    elif call.data == "nami":
        bot.answer_callback_query(call.id)
        send_nami_previews(chat_id)
    elif call.data == "yor":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "❤️ Yor Pack — coming soon.", reply_markup=main_menu())
    elif call.data == "boa":
        bot.answer_callback_query(call.id)
        send_boa_previews(chat_id)
    elif call.data == "bundle":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🔥 All Packs Bundle — coming soon.", reply_markup=main_menu())
    elif call.data == "about":
        bot.answer_callback_query(call.id)
        about_command(call.message)
    elif call.data == "custom":
        bot.answer_callback_query(call.id)
        bot.send_invoice(
            chat_id=chat_id,
            title="Custom Anime Image",
            description="1 custom AI anime-style image. Send your idea after payment.",
            invoice_payload="custom_image_750",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="Custom Image", amount=CUSTOM_IMAGE_STARS)],
        )


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=["successful_payment"])
def got_payment(message):
    payment = message.successful_payment
    if payment.invoice_payload == "nami_pack_99":
        try:
            update_stat("nami_sales")
        except Exception:
            pass
        deliver_nami_pack(message)
        return

    if payment.invoice_payload == "boa_hancock_pack_99":
        try:
            update_stat("boa_sales")
        except Exception:
            pass
        deliver_boa_pack(message)
        return
    if payment.invoice_payload == "custom_image_750":
        bot.send_message(
            message.chat.id,
            "✅ Payment received!\n\n"
            "Now send your custom image request in one message:\n\n"
            "1. Character idea or reference\n"
            "2. Outfit/style\n"
            "3. Pose or mood\n"
            "4. Wallpaper size if needed",
        )
        if ADMIN_ID:
            try:
                bot.send_message(
                    int(ADMIN_ID),
                    "💰 New paid Custom Image order!\n\n"
                    f"User: @{message.from_user.username or 'no_username'}\n"
                    f"User ID: {message.chat.id}\n"
                    f"Stars paid: {payment.total_amount}",
                )
            except Exception:
                pass


@bot.channel_post_handler(content_types=["document"])
def storage_channel_document(message):
    if not ADMIN_ID:
        return

    file_name = message.document.file_name or "document"
    lower_name = file_name.lower()

    if "nami" in lower_name:
        channel_variable = "NAMI_CHANNEL_ID"
        message_variable = "NAMI_MESSAGE_ID"
    elif "boa" in lower_name or "hancock" in lower_name:
        channel_variable = "BOA_CHANNEL_ID"
        message_variable = "BOA_MESSAGE_ID"
    else:
        channel_variable = "PACK_CHANNEL_ID"
        message_variable = "PACK_MESSAGE_ID"

    try:
        bot.send_message(
            int(ADMIN_ID),
            "📦 Storage channel document detected\n\n"
            f"{channel_variable}={message.chat.id}\n"
            f"{message_variable}={message.message_id}\n\n"
            f"File: {file_name}",
        )
    except Exception:
        pass

@bot.message_handler(content_types=["text"])
def handle_text(message):
    bot.send_message(message.chat.id, "Use the menu below 👇", reply_markup=main_menu())


print("Bot started - Nami + Boa premium packs")
bot.remove_webhook()
register_commands()
bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
