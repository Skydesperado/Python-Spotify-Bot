import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)

HELP_TEXT = "Send /preview Command For Getting <code>Preview</code> of Any Song and Then Give Me a Link From Spotify\n"

async def help_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=HELP_TEXT, reply_to_message_id=update.effective_message.id, parse_mode=ParseMode.HTML)
    except Exception as exception:
        logger.error(f"Error In start_handler: {exception}")
