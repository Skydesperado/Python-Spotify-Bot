import os
import logging
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utilities.spotify import get_track_info


logger = logging.getLogger(__name__)

async def download_file(url, file_name):
    try:
        if url is None:
            raise ValueError("URL Cannot be None")
        async with aiohttp.ClientSession() as request:
            async with request.get(url) as response:
                if response.status == 200:
                    with open(file_name, "wb") as file:
                        async for data in response.content.iter_any():
                            file.write(data)
                else:
                    logger.error(f"Failed To Download {url}")
    except Exception as exception:
        logger.error(f"Error Downloading {url}: {exception}")

async def download_track_preview(track_preview_url, track_preview_file, track_cover_url, track_cover_file):
    try:
        task_track = asyncio.create_task(download_file(track_preview_url, track_preview_file))
        task_cover = asyncio.create_task(download_file(track_cover_url, track_cover_file))
        await asyncio.gather(task_track, task_cover)
    except asyncio.CancelledError:
        logger.error("Download Task Was Cancelled")
    except Exception as exception:
        logger.error(f"Error Downloading Track or Cover: {exception}")

def delete_track_preview(track_preview_file, track_cover_file):
    try:
        os.remove(track_preview_file)
        os.remove(track_cover_file)
    except Exception as exception:
        logger.error(f"Error Deleting Track Preview or Cover: {exception}")

async def preview_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Give Me Any Song's Link From Spotify and I'll Send You Preview From That Song", reply_to_message_id=update.effective_message.id)
    except Exception as exception:
        logger.error(f"Error In preview_command_handler: {exception}")
    return "PREVIEW"

async def preview_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        track_url = update.message.text
        track_info = await get_track_info(track_url)
        track_preview_file = f"{track_info['track_title']}.mp3"
        track_cover_file = f"{track_info['track_title']}.jpg"
        await download_track_preview(track_preview_url=track_info["track_preview_url"], track_preview_file=track_preview_file, track_cover_url=track_info["track_cover_url"], track_cover_file=track_cover_file)
        with open(track_preview_file, "rb") as track_preview, open(track_cover_file, "rb") as track_cover:
            await context.bot.send_audio(chat_id=update.effective_chat.id, title=f"{track_info['track_title']} (Preview)", performer=track_info["track_artist"], audio=track_preview, thumbnail=track_cover)
        delete_track_preview(track_preview_file=track_preview_file, track_cover_file=track_cover_file)
    except Exception as exception:
        logger.error(f"Error In preview_message_handler: {exception}")
    return ConversationHandler.END

async def cancel_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Canceled", reply_to_message_id=update.effective_message.id)
    return ConversationHandler.END
