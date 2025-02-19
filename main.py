import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7858452797:AAFe1FUWWC9c67s1DlKfLauADLaxT8oBb3s"
bot = telebot.TeleBot(TOKEN)

# Holatlar
ASK_NAME, ASK_PHONE = range(2)

# Foydalanuvchi holatlari
user_states = {}

# Admin ID (o'zingizning Telegram ID'ingizni qo‘shing)
ADMIN_ID = 1938384946
ADMIN_CHAT_ID = -1002286917748  # Admin guruh ID

# Maxsus link
SPECIAL_LINK = "https://t.me/yoshtadbirkor_university/1073"


# Ism va familiya tekshirish (faqat harflar bo‘lishi kerak)
def is_valid_name(name):
    return all(x.isalpha() or x.isspace() for x in name)


@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "👋 Salom! Iltimos, ismingiz va familiyangizni kiriting:")
    user_states[chat_id] = ASK_NAME  # Holatni ASK_NAME ga o‘zgartirish


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == ASK_NAME)
def ask_name(message):
    chat_id = message.chat.id
    full_name = message.text.strip()

    if not is_valid_name(full_name):
        bot.send_message(chat_id, "⚠ Iltimos, faqat harflardan iborat ism va familiya kiriting!")
        return

    user_states[chat_id] = {"full_name": full_name, "step": ASK_PHONE}  # Keyingi bosqich
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))

    bot.send_message(chat_id, "📲 Endi telefon raqamingizni yuboring:", reply_markup=markup)


@bot.message_handler(
    func=lambda message: isinstance(user_states.get(message.chat.id), dict) and user_states[message.chat.id][
        "step"] == ASK_PHONE, content_types=["contact"])
def ask_phone(message):
    chat_id = message.chat.id
    user_data = user_states[chat_id]

    phone_number = message.contact.phone_number  # Faqat contact orqali olinadi
    full_name = user_data["full_name"]

    # Foydalanuvchiga tasdiqlash xabari
    bot.send_message(
        chat_id,
        f"✅ Rahmat, {full_name}!\n"
        f"📞 Sizning telefon raqamingiz: {phone_number}\n"
        f"🔗 Qo‘llanmaga kirish uchun mana bu linkni bosing: {SPECIAL_LINK}"
    )

    # Adminlarga xabar yuborish
    admin_message = (
        f"📥 *Yangi foydalanuvchi ma'lumotlari:*\n\n"
        f"👤 Ism: *{full_name}*\n"
        f"📞 Telefon: *{phone_number}*\n"
        f"🔗 [Qo‘llanmaga kirish]({SPECIAL_LINK})"
    )
    bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode="Markdown")

    # Foydalanuvchi ma'lumotlarini o‘chirish
    del user_states[chat_id]


@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "✅ Admin paneliga hush kelibsiz!")
    else:
        bot.send_message(message.chat.id, "⛔️ Siz admin emassiz!")


print("🤖 Bot ishga tushdi...")
bot.polling(none_stop=True)
