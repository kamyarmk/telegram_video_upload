import os


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token and Admin Chat ID
BOT_TOKEN = BOT_TOKEN
ADMIN_CHAT_ID = ADMIN_CHAT_ID

# Conversation states
ASK_NAME, ASk_AGE, ASK_INSTRUMENT, ASK_VIDEO = range(4)

# Dictionary to store user data
temp_data = {}

def welcome_new_user(update: Update, context: CallbackContext):
    if update.my_chat_member.new_chat_member.status == "member":
        chat_id = update.my_chat_member.chat.id
        user_name = update.my_chat_member.from_user.first_name
        welcome_text = (
            f"وقتتون بخیر /n"
            "به ربات تلگرامی آزاده شمس خوش آومدید.\n"
            "لطفا برای آپلود ویدیوی نوازندگی کودک خودتون دکمه شروع رو بزنید \n"
        )

        keyboard = [[InlineKeyboardButton("🚀 شروع کنید", callback_data="/start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=reply_markup)

def start(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    update.message.reply_text("اسم کودک خودتون رو وارد کنید")
    return ASK_NAME

def get_name(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    temp_data[user_id] = {'name': update.message.text}
    update.message.reply_text(" لطفا بگید چند سالشه")
    return ASk_AGE

def get_age(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    temp_data[user_id] = {'age': update.message.text}
    update.message.reply_text("سازی که مینوازه رو بنویسید")
    return ASK_INSTRUMENT

def get_instrument(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    temp_data[user_id] = {'instrument': update.message.text}
    update.message.reply_text("حالا میتونید ویدیو خودتون رو ارسال کنید. (توجه داشته باشید ویدیو حداکثر دو دقیقه باشه.)")
    return ASK_VIDEO

def get_video(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    video = update.message.video or update.message.document
    
    if not video:
        update.message.reply_text("Please send a valid video file.")
        return ASK_VIDEO
    
    user_name = temp_data.get(user_id, {}).get('name', 'Unknown User')
    user_age = temp_data.get(user_id, {}).get('age', 'Unknown Age')
    user_instrument = temp_data.get(user_id, {}).get('instrument', 'Unknown Instrument')

    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"New video uploaded by {user_name} ({user_id}).\n age : {user_age} \n instrument: {user_instrument}"
    )
    context.bot.send_video(chat_id=ADMIN_CHAT_ID, video=video.file_id)
    
    update.message.reply_text("مرسی که هنرنمایی کودک خودتون رو با ما به اشتراک گذاشتید به زودی بررسی می کنیم و …")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Process cancelled.")
    return ConversationHandler.END

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.status_update.my_chat_member, welcome_new_user))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            ASk_AGE: [MessageHandler(Filters.text & ~Filters.command, get_age)],
            ASK_INSTRUMENT: [MessageHandler(Filters.text & ~Filters.command, get_instrument)],
            ASK_VIDEO: [MessageHandler(Filters.video | Filters.document.video, get_video)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()