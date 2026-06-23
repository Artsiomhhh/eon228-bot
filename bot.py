import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

FREE_PACK_PATH = "free_pack.zip"
CUSTOM_IMAGE_STARS = 750

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
    if message.successful_payment.invoice_payload == "custom_image_15":
        user_states[message.chat.id] = "waiting_custom_description"

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
                f"User ID: {message.chat.id}\n"
                f"Stars paid: {message.successful_payment.total_amount}"
            )


@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    if user_states.get(chat_id) == "waiting_custom_description":
        user_states.pop(chat_id, None)

        username = message.from_user.username
        user_info = f"@{username}" if username else f"ID: {chat_id}"

        bot.send_message(
            chat_id,
            "✅ Your request has been received!\n\n"
            "I will review it and prepare your custom image.",
            reply_markup=main_menu()
        )

        if ADMIN_ID:
            bot.send_message(
                int(ADMIN_ID),
                "🎨 Custom Image Request Details\n\n"
                f"From: {user_info}\n"
                f"User ID: {chat_id}\n\n"
                f"Request:\n{text}"
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

            if ADMIN_ID:
                username = message.from_user.username
                user_info = f"@{username}" if username else f"ID: {chat_id}"

                bot.send_message(
                    int(ADMIN_ID),
                    "🎁 Free Pack downloaded\n\n"
                    f"User: {user_info}\n"
                    f"User ID: {chat_id}"
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
