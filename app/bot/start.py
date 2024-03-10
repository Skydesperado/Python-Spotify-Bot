import logging
from html import escape
from telegram.constants import ParseMode
from telegram import Update
from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)

async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.message.chat.first_name
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Welcome <i>{escape(user_first_name)}</i>!\n\nSend Me Link of Any Song You Like From Spotify and I'll Send It To You!\n\nUse /help Command For More Information", reply_to_message_id=update.effective_message.id, parse_mode=ParseMode.HTML)
    except Exception as exception:
        logger.error(f"Error In start_handler: {exception}")
