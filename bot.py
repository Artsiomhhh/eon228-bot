import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

FREE_PACK_PATH = "free_pack.zip"
user_states = {}


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 Free Pack")
    markup.add("💖 Nami Pack", "❤️ Yor Pack")
    markup.add("💙 Android 18 Pack", "🔥 All Packs Bundle")
    markup.add("🎨 Custom Image — $15")
    markup.add("ℹ️ About")
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🔥 Welcome to EgoEON AI Store\n\n"
        "Download exclusive AI anime wallpaper packs:\n\n"
        "🎁 Free Wallpapers\n"
        "💖 Nami Pack\n"
        "❤️ Yor Pack\n"
        "💙 Android 18 Pack\n"
        "🔥 Bundle Pack\n"
        "🎨 Custom Image — $15\n\n"
        "📱 All wallpapers are optimized for mobile devices.\n\n"
        "Choose a pack below 👇",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    if user_states.get(chat_id) == "waiting_custom_description":
        description = text
        user_states.pop(chat_id, None)

        username = message.from_user.username
        user_info = f"@{username}" if username else f"ID: {chat_id}"

        bot.send_message(
            chat_id,
            "✅ Your custom image request has been received!\n\n"
            "Price: $15\n"
            "I will review your request and prepare payment instructions soon.",
            reply_markup=main_menu()
        )

        if ADMIN_ID:
            bot.send_message(
                int(ADMIN_ID),
                "🎨 New Custom Image Request — $15\n\n"
                f"From: {user_info}\n"
                f"User ID: {chat_id}\n\n"
                f"Request:\n{description}"
            )

        return

    if text == "🎁 Free Pack":
        if os.path.exists(FREE_PACK_PATH):
            bot.send_message(chat_id, "🎁 Sending your free wallpaper pack...")
            with open(FREE_PACK_PATH, "rb") as file:
                bot.send_document(
                    chat_id,
                    file,
                    caption="🎁 Free Anime Wallpaper Pack by EgoEON AI"
                )
        else:
            bot.send_message(chat_id, "❌ free_pack.zip not found.")

    elif text == "💖 Nami Pack":
        bot.send_message(chat_id, "💖 Nami Pack — $3\n\nPayment system coming soon.")

    elif text == "❤️ Yor Pack":
        bot.send_message(chat_id, "❤️ Yor Pack — $3\n\nPayment system coming soon.")

    elif text == "💙 Android 18 Pack":
        bot.send_message(chat_id, "💙 Android 18 Pack — $3\n\nPayment system coming soon.")

    elif text == "🔥 All Packs Bundle":
        bot.send_message(chat_id, "🔥 All Packs Bundle — $7\n\nPayment system coming soon.")

    elif text == "🎨 Custom Image — $15":
        user_states[chat_id] = "waiting_custom_description"
        bot.send_message(
            chat_id,
            "🎨 Custom Anime Image — $15\n\n"
            "Send your request in one message:\n\n"
            "1. Character idea or reference\n"
            "2. Outfit/style\n"
            "3. Pose or mood\n"
            "4. Wallpaper size if needed\n\n"
            "Example:\n"
            "Anime girl with white hair, red eyes, black dress, dark cyberpunk city background."
        )

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


print("Bot started")
bot.infinity_polling()
