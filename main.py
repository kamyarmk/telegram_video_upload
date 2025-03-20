import os


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

from telegram import Update, Bot
from telegram.ext import Application, filters, Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token and Admin Chat ID


# Conversation states
ASK_NAME, ASK_AGE, ASK_LAND, ASK_INSTRUMENT, ASK_VIDEO = range(5)

# Dictionary to store user data
temp_data = {}

async def error_handler(update: object, context: CallbackContext):
    logging.error(f"Exception while handling an update: {context.error}")

# async def welcome_new_user(update: Update, context: CallbackContext):
#     if update.effective_chat is None:
#         return  # Prevent NoneType errors
#     chat_id = update.effective_chat.id
#     # user_name = update.my_chat_member.from_user.first_name
#     welcome_text = (
#         f"وقتتون بخیر \n به ربات تلگرامی آزاده شمس خوش آومدید.\n لطفا برای آپلود ویدیوی نوازندگی کودک خودتون دکمه شروع رو بزنید \n"
#     )
    
#     keyboard = [[InlineKeyboardButton("🚀 شروع کنید", callback_data="start_command")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=reply_markup)

async def start_command_callback(update: Update, context: CallbackContext):
    """Handles the button press for the Start command."""
    query = update.callback_query
    await query.answer()  # Use await for async

    start_text = "نام و نام خانوادگی کودک خودتون رو وارد کنید"

    await query.message.reply_text(start_text)
    await update.message.reply_text(" لطفا بگید چند سالشه")
    return ASK_NAME  # Make sure this matches your state flow

async def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    chat_id = update.effective_chat.id
    keyboard = [[InlineKeyboardButton("🚀 شروع کنید", callback_data="start_command")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = "وقتتون بخیر \n به ارکستر دانژه خوش اومدید.\nلطفا برای آپلود ویدیوی نوازندگی کودک خودتون دکمه شروع رو بزنید"
    # await update.message.reply_text("وقتتون بخیر \n به ربات تلگرامی آزاده شمس خوش آومدید.\n لطفا برای آپلود ویدیوی نوازندگی کودک خودتون دکمه شروع رو بزنید \n")
    await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=reply_markup)

    return ASK_NAME

async def get_name(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    temp_data[user_id] = {'name': update.message.text}
    await update.message.reply_text(" لطفا بگید چند سالشه")
    return ASK_AGE

async def get_age(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    temp_data[user_id]['age'] = update.message.text
    await update.message.reply_text("کشور محل اقامتتون رو بنویسید")
    return ASK_LAND

async def get_country(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    temp_data[user_id]['land'] = update.message.text
    await update.message.reply_text("سازی که مینوازه رو بنویسید")
    return ASK_INSTRUMENT

async def get_instrument(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    temp_data[user_id]['instrument'] = update.message.text
    await update.message.reply_text("حالا میتونید ویدیو خودتون رو ارسال کنید. (توجه داشته باشید ویدیو حداکثر دو دقیقه باشه.)")
    return ASK_VIDEO

async def get_video(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    video = update.message.video or update.message.document

    if not video:
        await update.message.reply_text("لطفا ویدیوی معتبر ارسال کنید.")
        return ASK_VIDEO

    user_info = temp_data.get(user_id, {})
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"ویدیوی جدید از {user_info.get('name', 'Unknown')},\n سن: {user_info.get('age', 'Unknown')},\n کشور: {user_info.get('land', 'Unknown')} \n ساز: {user_info.get('instrument', 'Unknown')} \n "
    )
    await context.bot.send_video(chat_id=ADMIN_CHAT_ID, video=video.file_id)
    await update.message.reply_text("مرسی که هنرنمایی کودک خودتون رو با ما به اشتراک گذاشتید به زودی بررسی می کنیم🙂")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Process cancelled.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)
    # Add handlers
    # app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.ALL, welcome_new_user))
    app.add_handler(CallbackQueryHandler(start_command_callback, pattern="start_command"))

    # updater = Updater(BOT_TOKEN, use_context=True)
    # dp = updater.dispatcher
    # dp.add_handler(MessageHandler(Filters.all, welcome_new_user))
    # dp.add_handler(CallbackQueryHandler(start_command_callback, pattern="start_command"))

    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            ASK_LAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
            ASK_INSTRUMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_instrument)],
            ASK_VIDEO: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, get_video)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    # Start polling
    app.run_polling()
    
    # dp.add_handler(conv_handler)
    # updater.start_polling()
    # updater.idle()

if __name__ == "__main__":
    main()