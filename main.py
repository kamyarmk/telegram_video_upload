import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Token and Admin Chat ID
BOT_TOKEN = BOT_TOKEN
ADMIN_CHAT_ID = ADMIN_CHAT_ID

# Conversation states
ASK_NAME, ASK_VIDEO = range(2)

# Dictionary to store user data
temp_data = {}

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Hello! Please enter your name before uploading a video.")
    return ASK_NAME

def get_name(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    temp_data[user_id] = {'name': update.message.text}
    update.message.reply_text("Thank you! Now, please upload your video.")
    return ASK_VIDEO

def get_video(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    video = update.message.video or update.message.document
    
    if not video:
        update.message.reply_text("Please send a valid video file.")
        return ASK_VIDEO
    
    user_name = temp_data.get(user_id, {}).get('name', 'Unknown User')
    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"New video uploaded by {user_name} ({user_id})."
    )
    context.bot.send_video(chat_id=ADMIN_CHAT_ID, video=video.file_id)
    
    update.message.reply_text("Your video has been uploaded and will be reviewed. Thank you!")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Process cancelled.")
    return ConversationHandler.END

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            ASK_VIDEO: [MessageHandler(Filters.video | Filters.document.video, get_video)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()