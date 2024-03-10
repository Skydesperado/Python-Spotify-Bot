import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from bot.start import start_command_handler
from bot.help import help_command_handler
from bot.preview import preview_command_handler, preview_message_handler, cancel_command_handler
from bot.download import download_track_message_handler


def configure_logger():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    logging.getLogger("httpx").setLevel(level=logging.WARNING)

def configure_bot():
    application = ApplicationBuilder().token(os.environ.get("TOKEN")).build()
    preview_handler = ConversationHandler(
        entry_points=[
            CommandHandler("preview", preview_command_handler),
            ], 
        states={
            "PREVIEW": [
                MessageHandler(filters.TEXT & ~filters.COMMAND, preview_message_handler),
                ],
        },
        fallbacks=[
            CommandHandler("end", cancel_command_handler),
        ],
        allow_reentry=True,
    )
    application.add_handler(CommandHandler("start", start_command_handler))
    application.add_handler(CommandHandler("help", help_command_handler))
    application.add_handler(preview_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_track_message_handler))
    application.run_polling()
