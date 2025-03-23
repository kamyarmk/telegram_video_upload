import os
from telegram import Update, Bot
from telegram.ext import Application, filters, Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging


# Env Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
SET_LANGUAGE, START_COMMAND, ASK_NAME, ASK_AGE, ASK_LAND, ASK_INSTRUMENT, ASK_VIDEO = range(7)

#Dictinary for the texts
user_language = {}

LANGUAGES = {
    "fa": "فارسی 🇮🇷",  # Persian
    "en": "English 🇬🇧"
}
content = {
    "fa" : {
        "Welcome" : "\u200F وقتتون بخیر \n به ارکستر دانژه خوش اومدید.\nلطفا برای آپلود ویدیوی نوازندگی کودک خودتون دکمه شروع رو بزنید",
        "Button" : "\u200F 🚀 شروع کنید",
        "ASK_NAME" : "\u200F نام و نام خانوادگی کودک خودتون رو وارد کنید",
        "ASK_AGE" : "\u200F لطفا بگید چند سالشه",
        "ASK_LAND" : "\u200F کشور محل اقامتتون رو بنویسید",
        "ASK_INSTRUMENT" : "\u200F سازی که مینوازه رو بنویسید",
        "ASK_VIDEO" : "\u200F حالا میتونید ویدیو خودتون رو ارسال کنید. (توجه داشته باشید ویدیو حداکثر دو دقیقه باشه.)",
        "Video_Error" : "\u200F لطفا ویدیوی معتبر ارسال کنید.",
        "Upload_success": "\u200F مرسی که هنرنمایی کودک خودتون رو با ما به اشتراک گذاشتید به زودی بررسی می کنیم🙂",
        "Cancel" : "\u200F فرآیند لغو شد."
    },
    "en" : {
        "Welcome" : "Good morning \n Welcome to the Danje Orchestra.\nPlease click the start button to upload a video of your child performing",
        "Button" : "🚀 Start",
        "ASK_NAME" : "Enter your child's first and last name",
        "ASK_AGE" : "Please tell me how old they are",
        "ASK_LAND" : "Write your country of residence",
        "ASK_INSTRUMENT" : "Write the instrument they play",
        "ASK_VIDEO" : "You can now submit your video. (Please note that the video should be a maximum of two minutes.)",
        "Video_Error" : "Please submit a valid video.",
        "Upload_success": "Thank you for sharing your child's performance with us. We'll check it out soon 🙂",
        "Cancel" : "Process canceled."
    },
}

# Dictionary to store user data
temp_data = {}

# Error Handeling
async def error_handler(update: object, context: CallbackContext):
    logging.error(f"Exception while handling an update: {context.error}")

#Start of the Application
async def start(update: Update, context: CallbackContext) -> int:
    """Ask the user to select a language before starting."""
    chat_id = update.effective_chat.id
    keyboard = [
        [InlineKeyboardButton(LANGUAGES["fa"], callback_data="lang_fa")],
        [InlineKeyboardButton(LANGUAGES["en"], callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text="🌍 لطفاً زبان خود را انتخاب کنید:\n🌍 Please choose your language:", reply_markup=reply_markup)
    return SET_LANGUAGE 

#Language Options
async def set_language(update: Update, context: CallbackContext) -> int:
    """Stores the user's selected language and moves to the next step."""
    query = update.callback_query
    user_id = query.from_user.id
    selected_lang = query.data.split("_")[1]  # "fa" or "en"

    # Store the language preference
    user_language[user_id] = selected_lang

    response = content[selected_lang]["Welcome"]
    start_button = InlineKeyboardButton(content[selected_lang]["Button"], callback_data="start_command")

    reply_markup = InlineKeyboardMarkup([[start_button]])

    await query.answer()
    await query.message.edit_text(response, reply_markup=reply_markup)
    return START_COMMAND


async def start_command_callback(update: Update, context: CallbackContext) -> int:
    """Handles the button press for the Start command."""
    query = update.callback_query
    user_id = query.from_user.id
    lang = user_language.get(user_id, "fa")  # Default to Persian

    await query.answer()
    await query.message.reply_text(content[lang]["ASK_NAME"])
    
    return ASK_NAME

#Main State of the app Start
async def get_name(update: Update, context: CallbackContext) -> int:
    print("done2")
    user_id = update.message.from_user.id
    lang = user_language.get(user_id, "fa")
    
    temp_data[user_id] = {'name': update.message.text}
    await update.message.reply_text(content[lang]["ASK_AGE"])
    return ASK_AGE

async def get_age(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    lang = user_language.get(user_id, "fa")

    temp_data[user_id]['age'] = update.message.text
    await update.message.reply_text(content[lang]["ASK_LAND"])
    return ASK_LAND

async def get_country(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    lang = user_language.get(user_id, "fa")

    temp_data[user_id]['land'] = update.message.text
    await update.message.reply_text(content[lang]["ASK_INSTRUMENT"])
    return ASK_INSTRUMENT

async def get_instrument(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    lang = user_language.get(user_id, "fa")

    temp_data[user_id]['instrument'] = update.message.text
    await update.message.reply_text(content[lang]["ASK_VIDEO"])
    return ASK_VIDEO

#Video Upload
async def get_video(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    lang = user_language.get(user_id, "fa")

    video = update.message.video or update.message.document

    if not video:
        await update.message.reply_text(content[lang]["Video_Error"])
        return ASK_VIDEO

    user_info = temp_data.get(user_id, {})
    #Sending the Datas to the Admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"\u200F ویدیوی جدید از {user_info.get('name', 'Unknown')},\n سن: {user_info.get('age', 'Unknown')},\n کشور: {user_info.get('land', 'Unknown')} \n ساز: {user_info.get('instrument', 'Unknown')} \n "
    )
    await context.bot.send_video(chat_id=ADMIN_CHAT_ID, video=video.file_id)
    await update.message.reply_text(content[lang]["Upload_success"])
    return ConversationHandler.END
#Proccess Cancelation
async def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    lang = user_language.get(user_id, "fa")

    await update.message.reply_text(content[lang]["Cancel"])
    return ConversationHandler.END

def main():
    # App Define
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)

    #States Define
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],  
        states={
            SET_LANGUAGE: [CallbackQueryHandler(set_language, pattern="^lang_.*$")],  
            START_COMMAND: [CallbackQueryHandler(start_command_callback, pattern="start_command")], 
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

if __name__ == "__main__":
    main()