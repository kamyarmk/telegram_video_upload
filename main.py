import os
from telegram import Update, Bot
from telegram.ext import Application, filters, Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging


# Env Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
MAIN_MENU, SET_LANGUAGE, START_COMMAND, ASK_NAME, ASK_AGE, ASK_LAND, ASK_INSTRUMENT, ASK_VIDEO = range(8)

#Dictinary for the texts
user_language = {}
stored_lang = ""

LANGUAGES = {
    "fa": "فارسی 🇮🇷",  # Persian
    "en": "English 🇬🇧"
}
content = {
    "fa" : {
        "Welcome" : "\u200F وقتتون بخیر \n به ارکستر دانژه خوش اومدید.\nلطفا برای آپلود ویدیوی نوازندگی کودک خودتون دکمه شروع رو بزنید \n\n",
        "Button" : "\u200F 🚀 شروع کنید",
        "ASK_NAME" : "\u200F نام و نام خانوادگی کودک خودتون رو وارد کنید \n\n",
        "ASK_AGE" : "\u200Fلطفا بگید چند سالشه \n\n",
        "ASK_LAND" : "\u200F کشور محل اقامتتون رو بنویسید \n\n",
        "ASK_INSTRUMENT" : "\u200F سازی که مینوازه رو بنویسید \n\n",
        "ASK_VIDEO" : "\u200F حالا میتونید ویدیو خودتون رو ارسال کنید. (توجه داشته باشید ویدیو حداکثر دو دقیقه باشه.) \n\n",
        "Video_Error" : "\u200F لطفا ویدیوی معتبر ارسال کنید. \n\n",
        "Upload_success": "\u200F مرسی که هنرنمایی کودک خودتون رو با ما به اشتراک گذاشتید به زودی بررسی می کنیم🙂 \n\n",
        "Cancel" : "\u200F فرآیند لغو شد. \n\n",
        "Video_upload_btn" : "\u200F ⭐ شروع آپلود",
        "About_btn" : "\u200F ℹ️ درباره",
        "Contact_Us_btn" : "\u200F 📞 تماس با ما",
        "Cancel_btn" : "\u200F ❌ لغو",
        "Processing": "\u200F در حال پردازش... \n\n",
        "Invalid_Option": "\u200F گزینه نامعتبر! لطفاً از منو انتخاب کنید. \n\n",
        "Select_Option": "لطفاً یک گزینه را انتخاب کنید: \n\n"
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
        "Cancel" : "Process canceled.",
        "Video_upload_btn" : "⭐ Start Upload",
        "About_btn" : "ℹ️ About",
        "Contact_Us_btn" : "📞 Contact Us",
        "Cancel_btn" : "❌ Cancel",
        "Invalid_Option": "Invalid option! Please choose from the menu.",
        "Processing": "Processing your request...",
        "Select_Option": "Please select an option:"
    },
}

# Dictionary to store user data
temp_data = {}

# Error Handeling
async def error_handler(update: object, context: CallbackContext) -> int:
    logging.error(f"Exception while handling an update: {context.error}")

# Commands menu
async def show_main_menu(update: Update, context: CallbackContext, selected_lang) -> int:
    user_id = update.message.from_user.id
    print(user_id)
    
    # lang = user_language.get(user_id, "fa")  # Default to Persian
    lang = selected_lang  # Default to Persian
    """Displays the main menu options."""
    keyboard = [
        [content[lang]["Contact_Us_btn"], content[lang]["About_btn"]],
        [content[lang]["Video_upload_btn"], content[lang]["Cancel_btn"]]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(content[lang]["Select_Option"], reply_markup=reply_markup)

async def set_bot_commands(app):
    """Sets up bot commands for quick access in the menu."""
    commands = [
        ("start", "Restart the bot"),
        ("upload", "Upload a video"),
        ("language", "Change language"),
        ("about", "About this bot"),
        ("cancel", "Cancel operation")
    ]
    await app.bot.set_my_commands(commands)

async def handle_menu(update: Update, context: CallbackContext) -> int:
    """Handles user selection from the main menu."""
    text = update.message.text

    user_id = update.message.from_user.id
    lang = user_language.get(user_id, "fa")

    print(lang)

    if text == content[lang]["Contact_Us_btn"]:
        await update.message.reply_text("This bot allows you to upload videos for review.")
        return MAIN_MENU
    elif text == content[lang]["Video_upload_btn"]:
        await update.message.reply_text(content[lang]["Processing"], reply_markup=ReplyKeyboardRemove())

        await update.message.reply_text(content[lang]["ASK_NAME"])
        return ASK_NAME  # Transition to the next step
    elif text == content[lang]["About_btn"]:
        await update.message.reply_text("This bot allows you to upload videos for review.")
        return MAIN_MENU
    elif text == content[lang]["Cancel_btn"]:
        await update.message.reply_text(content[lang]["Processing"], reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text(content[lang]["Cancel"])
        return ConversationHandler.END
    else:
        await update.message.reply_text(content[lang]["Invalid_Option"])
        return MAIN_MENU

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
    stored_lang = selected_lang


    response = content[selected_lang]["Welcome"]
    # start_button = InlineKeyboardButton(content[selected_lang]["Button"], callback_data="start_command")

    # reply_markup = InlineKeyboardMarkup([[start_button]])

    await query.answer()
    await query.message.edit_text(response)
    await show_main_menu(query, context, selected_lang)
    return MAIN_MENU


async def start_command_callback(update: Update, context: CallbackContext) -> int:
    """Handles the button press for the Start command."""
    query = update.callback_query
    user_id = query.from_user.id
    lang = user_language.get(user_id, "fa")  # Default to Persian
    
    await query.answer()
    await update.message.reply_text(content[lang]["Processing"], reply_markup=ReplyKeyboardRemove())
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
    set_bot_commands(app)

    #States Define
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],  
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
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