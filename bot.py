from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater,ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

import os
import requests
from PIL import Image
from io import BytesIO
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
WAITING_FOR_IMAGE = range(1)

token = os.environ["TELEGRAM_BOT_TOKEN"]
def say_name(update, context):
    update.message.reply_text('Hello! I am your bot.')
    
def connect_server(update,context):
    answer = requests.get(url = "https://poc-fastapi-server.onrender.com").json()
    update.message.reply_text(f'got the answer: {answer}')

# def get_img(update,context):
#     if len(update.message.photo)>0:
#         photo_file = update.message.photo[-1].get_file()
#         print('photo_file: ', photo_file)
#         photo_bytes = requests.get(photo_file.file_path).content
#         image = Image.open(BytesIO(photo_bytes))
#     update.message.reply_text('got img')
    
def log_message(update, context):
    user = update.message.from_user
    logger.info(f"Message from {user.username} ({user.id}): {update.message.text}")
    
def img_command(update, context):
    update.message.reply_text('Please send the image you want to process.')
    return WAITING_FOR_IMAGE

def receive_image(update, context):
    # Check if the update contains a photo
    if update.message.photo:
        # Get the file object for the last (highest resolution) photo
        photo_file = update.message.photo[-1].get_file()
        # Download the image file
        photo_bytes = requests.get(photo_file.file_path).content
        # Open the image file (optional, for further processing or validation)
        image = Image.open(BytesIO(photo_bytes))
        files = {"file": image}
        response = requests.post("https://poc-fastapi-server.onrender.com/img", files=files)
        # Acknowledge the receipt of the image
        update.message.reply_text('Image received successfully!')
    else:
        update.message.reply_text('No image received. Please send an image.')

    # End the conversation
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def main() -> None:
    updater = Updater(token)

    # Get the dispatcher to register handlers
    # Then, we register each handler and the conditions the update must meet to trigger it
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler("hi", say_name))
    # dispatcher.add_handler(CommandHandler("img", get_img))
    dispatcher.add_handler(CommandHandler("get", connect_server))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('img', img_command)],
        states={
            WAITING_FOR_IMAGE: [MessageHandler(Filters.photo, receive_image)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)
    # Start the Bot
    dispatcher.add_handler(MessageHandler(Filters.all, log_message))  # Log all messages
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
