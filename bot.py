import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎁 Free Pack")
    markup.add("💖 Nami Pack", "❤️ Yor Pack")
    markup.add("💙 Android 18 Pack", "🔥 All Packs Bundle")

    bot.send_message(
        message.chat.id,
        "Welcome to EgoEON AI Store ✨\n\nChoose your anime wallpaper pack:",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text

    if text == "🎁 Free Pack":
        bot.send_message(message.chat.id, "🎁 Free Pack is coming soon.")

    elif text == "💖 Nami Pack":
        bot.send_message(message.chat.id, "💖 Nami Pack — $3\nPayment coming soon.")

    elif text == "❤️ Yor Pack":
        bot.send_message(message.chat.id, "❤️ Yor Pack — $3\nPayment coming soon.")

    elif text == "💙 Android 18 Pack":
        bot.send_message(message.chat.id, "💙 Android 18 Pack — $3\nPayment coming soon.")

    elif text == "🔥 All Packs Bundle":
        bot.send_message(message.chat.id, "🔥 All Packs Bundle — $7\nPayment coming soon.")

    else:
        bot.send_message(message.chat.id, "Choose a pack from the menu 👇")


print("Bot started")
bot.infinity_polling()
