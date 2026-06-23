import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

FREE_PACK_PATH = "free_pack.zip"


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add("🎁 Free Pack")
    markup.add("💖 Nami Pack", "❤️ Yor Pack")
    markup.add("💙 Android 18 Pack", "🔥 All Packs Bundle")
    markup.add("ℹ️ About")

    bot.send_message(
        message.chat.id,
        "🔥 Welcome to EgoEON AI Store\n\n"
        "Download exclusive AI anime wallpaper packs:\n\n"
        "🎁 Free Wallpapers\n"
        "💖 Nami Pack\n"
        "❤️ Yor Pack\n"
        "💙 Android 18 Pack\n"
        "🔥 Bundle Pack\n\n"
        "📱 All wallpapers are optimized for mobile devices.\n\n"
        "Choose a pack below 👇",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text

    if text == "🎁 Free Pack":
        if os.path.exists(FREE_PACK_PATH):
            bot.send_message(message.chat.id, "🎁 Sending your free wallpaper pack...")
            with open(FREE_PACK_PATH, "rb") as file:
                bot.send_document(
                    message.chat.id,
                    file,
                    caption="🎁 Free Anime Wallpaper Pack by EgoEON AI"
                )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Free pack file not found.\n\nAdmin needs to upload free_pack.zip."
            )

    elif text == "💖 Nami Pack":
        bot.send_message(
            message.chat.id,
            "💖 Nami Pack — $3\n\nPayment system coming soon."
        )

    elif text == "❤️ Yor Pack":
        bot.send_message(
            message.chat.id,
            "❤️ Yor Pack — $3\n\nPayment system coming soon."
        )

    elif text == "💙 Android 18 Pack":
        bot.send_message(
            message.chat.id,
            "💙 Android 18 Pack — $3\n\nPayment system coming soon."
        )

    elif text == "🔥 All Packs Bundle":
        bot.send_message(
            message.chat.id,
            "🔥 All Packs Bundle — $7\n\nPayment system coming soon."
        )

    elif text == "ℹ️ About":
        bot.send_message(
            message.chat.id,
            "EgoEON AI creates anime wallpaper packs.\n\n"
            "✨ HD quality\n"
            "📱 Mobile optimized\n"
            "🎨 AI anime artwork\n"
            "🎁 Free and premium packs\n\n"
            "New packs are added regularly."
        )

    else:
        bot.send_message(message.chat.id, "Choose a pack from the menu 👇")


print("Bot started")
bot.infinity_polling()
