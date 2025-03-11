import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7924814725:AAE2c9LAKjfoVEblPSzdO12U8QVWd6ARXic"
bot = telebot.TeleBot(TOKEN)

# Holatlar
ASK_NAME, ASK_PHONE = range(2)

# Foydalanuvchi holatlari va chat_id ro‘yxati
user_states = {}
user_chat_ids = set()
broadcast_message_content = {}
admin_states = {}  # Admin holatini saqlash uchun qo'shildi

# Admin ID va guruh ID
ADMIN_ID = 1938384946
ADMIN_CHAT_ID = "@farnexdev"

# Maxsus link
SPECIAL_LINK = "https://t.me/yoshtadbirkor_university/1073"

# Ism va familiya tekshirish
def is_valid_name(name):
    return all(x.isalpha() or x.isspace() for x in name)

# Barcha foydalanuvchilarga xabar yuborish funksiyasi
def broadcast_message(chat_ids, message):
    success_count = 0
    for chat_id in chat_ids:
        try:
            if message.content_type == "text":
                bot.send_message(chat_id, message.text)
            elif message.content_type == "photo":
                bot.send_photo(chat_id, message.photo[-1].file_id, caption=message.caption or "")
            elif message.content_type == "video":
                bot.send_video(chat_id, message.video.file_id, caption=message.caption or "")
            elif message.content_type == "document":
                bot.send_document(chat_id, message.document.file_id, caption=message.caption or "")
            elif message.content_type == "audio":
                bot.send_audio(chat_id, message.audio.file_id, caption=message.caption or "")
            elif message.content_type == "voice":  # Ovozli xabar qo'shildi
                bot.send_voice(chat_id, message.voice.file_id, caption=message.caption or "")
            elif message.content_type == "sticker":
                bot.send_sticker(chat_id, message.sticker.file_id)
            success_count += 1
        except Exception as e:
            print(f"Xabar yuborishda xato {chat_id}: {e}")
    return success_count

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "👋 Salom! Iltimos, ismingiz va familiyangizni kiriting:")
    user_states[chat_id] = ASK_NAME
    user_chat_ids.add(chat_id)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == ASK_NAME)
def ask_name(message):
    chat_id = message.chat.id
    full_name = message.text.strip()

    if not is_valid_name(full_name):
        bot.send_message(chat_id, "⚠ Iltimos, faqat harflardan iborat ism va familiya kiriting!")
        return

    user_states[chat_id] = {"full_name": full_name, "step": ASK_PHONE}
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))
    bot.send_message(chat_id, "📲 Endi telefon raqamingizni yuboring:", reply_markup=markup)

@bot.message_handler(
    func=lambda message: isinstance(user_states.get(message.chat.id), dict) and user_states[message.chat.id][
        "step"] == ASK_PHONE, content_types=["contact"])
def ask_phone(message):
    chat_id = message.chat.id
    user_data = user_states[chat_id]

    phone_number = message.contact.phone_number
    full_name = user_data["full_name"]

    bot.send_message(
        chat_id,
        f"✅ Rahmat, {full_name}!\n"
        f"📞 Sizning telefon raqamingiz: {phone_number}\n"
        f"🔗 Qo‘llanmaga kirish uchun mana bu linkni bosing: {SPECIAL_LINK}"
    )

    admin_message = (
        f"📥 *Yangi foydalanuvchi ma'lumotlari:*\n\n"
        f"👤 Ism: *{full_name}*\n"
        f"📞 Telefon: *{phone_number}*\n"
        f"🔗 [Qo‘llanmaga kirish]({SPECIAL_LINK})"
    )
    bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode="Markdown")

    del user_states[chat_id]

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔️ Siz admin emassiz!")
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📩 Xabar yuborish"))
    bot.send_message(message.chat.id, "✅ Admin paneliga hush kelibsiz!", reply_markup=markup)
    admin_states[message.chat.id] = None  # Holatni boshlang'ich holatga qaytarish

@bot.message_handler(func=lambda message: message.text == "📩 Xabar yuborish" and message.chat.id == ADMIN_ID)
def handle_broadcast_request(message):
    bot.send_message(message.chat.id, "✍️ Barcha foydalanuvchilarga yuboriladigan xabarni yuboring (matn, rasm, video, fayl, ovoz yoki stiker):")
    admin_states[message.chat.id] = "waiting_for_broadcast"  # Xabar kutilmoqda

@bot.message_handler(content_types=["text", "photo", "video", "document", "audio", "voice", "sticker"],
                    func=lambda message: message.chat.id == ADMIN_ID and
                    admin_states.get(message.chat.id) == "waiting_for_broadcast")
def prepare_broadcast(message):
    broadcast_message_content[message.chat.id] = message
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_broadcast"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_broadcast")
    )

    preview_text = "📤 Yuboriladigan xabar\nTasdiqlaysizmi?"
    if message.content_type == "text":
        bot.send_message(message.chat.id, f"📤 Yuboriladigan xabar:\n{message.text}\n\nTasdiqlaysizmi?", reply_markup=markup)
    elif message.content_type == "photo":
        bot.send_photo(message.chat.id, message.photo[-1].file_id, caption=message.caption or preview_text, reply_markup=markup)
    elif message.content_type == "video":
        bot.send_video(message.chat.id, message.video.file_id, caption=message.caption or preview_text, reply_markup=markup)
    elif message.content_type == "document":
        bot.send_document(message.chat.id, message.document.file_id, caption=message.caption or preview_text, reply_markup=markup)
    elif message.content_type == "audio":
        bot.send_audio(message.chat.id, message.audio.file_id, caption=message.caption or preview_text, reply_markup=markup)
    elif message.content_type == "voice":
        bot.send_voice(message.chat.id, message.voice.file_id, caption=message.caption or preview_text, reply_markup=markup)
    elif message.content_type == "sticker":
        bot.send_sticker(message.chat.id, message.sticker.file_id)
        bot.send_message(message.chat.id, preview_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["confirm_broadcast", "cancel_broadcast"])
def handle_broadcast_confirmation(call):
    if call.message.chat.id != ADMIN_ID:
        bot.answer_callback_query(call.id)
        return

    if call.data == "confirm_broadcast":
        message = broadcast_message_content.get(call.message.chat.id)
        if message:
            sent_count = broadcast_message(user_chat_ids, message)
            bot.send_message(call.message.chat.id, f"✅ Xabar {sent_count} ta foydalanuvchiga yuborildi!")
            del broadcast_message_content[call.message.chat.id]
    elif call.data == "cancel_broadcast":
        if call.message.chat.id in broadcast_message_content:
            del broadcast_message_content[call.message.chat.id]
        bot.send_message(call.message.chat.id, "❌ Xabar yuborish bekor qilindi.")

    admin_states[call.message.chat.id] = None  # Holatni tozalash
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

print("🤖 Bot ishga tushdi...")
bot.polling(none_stop=True)
