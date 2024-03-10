import os
import logging
import base64
import aiohttp


logger = logging.getLogger(__name__)

async def get_access_token():
    try:
        url = "https://accounts.spotify.com/api/token"
        client_credentials = f"{os.environ.get('SPOTIFY_CLIENT_ID')}:{os.environ.get('SPOTIFY_CLIENT_SECRET')}"
        headers = {
            "Authorization": "Basic " + base64.b64encode(client_credentials.encode("utf-8")).decode("utf-8"),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
        }
        async with aiohttp.ClientSession() as request:
            async with request.post(url, headers=headers, data=data) as response:
                response.raise_for_status()
                return (await response.json())["access_token"]
    except Exception as exception:
        logger.error(f"Error Getting Access Token: {exception}")
        return None

async def get_track_info(track_url):
    try:
        if "open.spotify.com/track/" in track_url:
            track_id = track_url.split("/")[-1].split("?")[0]
    except Exception as exception:
        logger.error(f"Invalid Track URL: {exception}")
        return None
    try:
        spotify_api_url = f"https://api.spotify.com/v1/tracks/{track_id}"
        headers = {
            "Authorization": f"Bearer {await get_access_token()}"
        }
        async with aiohttp.ClientSession() as request:
            async with request.get(spotify_api_url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                track_title = data["name"]
                track_artist = data["artists"][0]["name"]
                track_preview_url = data["preview_url"]
                track_cover_url = data["album"]["images"][0]["url"]
                album_title = data["album"]["name"]
                release_date = data["album"]["release_date"]
                return {
                    "track_title": track_title, 
                    "track_artist": track_artist,  
                    "track_preview_url": track_preview_url,
                    "track_cover_url": track_cover_url,
                    "album_title": album_title,
                    "release_date": release_date
                }
    except Exception as exception:
        logger.error(f"Error Fetching Track Info: {exception}")
        return None

async def get_track_download_link(track_url):
    rapid_api_url = "https://spotify-downloader6.p.rapidapi.com/spotify/"
    headers = {
        "X-RapidAPI-Key": os.environ.get("RAPID_API_KEY"),
        "X-RapidAPI-Host": os.environ.get("RAPID_API_HOST")
    }
    params = {
        "spotifyUrl": f"{track_url}"
    }
    async with aiohttp.ClientSession() as request:
        async with request.get(rapid_api_url, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            track_download_link = data["download_link"]
            return track_download_link
