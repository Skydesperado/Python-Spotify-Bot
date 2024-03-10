import os
import logging
import asyncio
import aiohttp
import eyed3
from html import escape
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from utilities.spotify import get_track_info, get_track_download_link


logger = logging.getLogger(__name__)

async def download_file(url, file_name):
    try:
        async with aiohttp.ClientSession() as request:
            async with request.get(url) as response:
                if response.status == 200:
                    with open(file_name, "wb") as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)
                else:
                    logger.error(f"Failed To Download {url}")
    except Exception as exception:
        logger.error(f"Error Downloading {url}: {exception}")

async def download_track(track_download_link, track_file, track_cover_url, track_cover_file):
    try:
        async with aiohttp.ClientSession() as request:
            tasks = [
                download_file(track_cover_url, track_cover_file),
                download_file(track_download_link, track_file),
            ]
            await asyncio.gather(*tasks)      
        audiofile = eyed3.load(track_file)
        if audiofile.tag is not None:
            if audiofile.tag.images:
                image_frame_string = str(audiofile.tag.images[0])
                audiofile.tag.images.remove(image_frame_string)
            audiofile.tag.save(version=eyed3.id3.ID3_V2_4)
    except asyncio.CancelledError:
        logger.error("Download Task Was Cancelled")
    except Exception as exception:
        logger.error(f"Error Downloading Track or Cover: {exception}")

def delete_track(track_file, track_cover_file):
    try:
        os.remove(track_file)
        os.remove(track_cover_file)
    except Exception as exception:
        logger.error(f"Error Deleting Track or Cover: {exception}")

async def generate_track_caption(track_info):
    caption = f"🎵 Track Title: <b>{escape(track_info['track_title'])}</b>\n👤 Artist: <i>{escape(track_info['track_artist'])}</i>\n💽 Album: {escape(track_info['album_title'])}\n📅 Release Date: {escape(track_info['release_date'])}"
    return caption

async def download_track_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        track_url = update.message.text
        track_info = await get_track_info(track_url)
        track_download_link = await get_track_download_link(track_url)
        track_file = f"{track_info['track_title']}.mp3"
        track_cover_file = f"{track_info['track_title']}.jpg"
        await download_track(track_download_link=track_download_link, track_file=track_file, track_cover_url=track_info["track_cover_url"], track_cover_file=track_cover_file)
        with open(track_file, "rb") as track, open(track_cover_file, "rb") as track_cover:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=track_cover, caption=await generate_track_caption(track_info), parse_mode=ParseMode.HTML)
                await context.bot.send_audio(chat_id=update.effective_chat.id, title=track_info["track_title"], performer=track_info["track_artist"], audio=track, thumbnail=track_cover)
        delete_track(track_file, track_cover_file)
    except Exception as exception:
        logger.error(f"Error In download_track_message_handler: {exception}")
