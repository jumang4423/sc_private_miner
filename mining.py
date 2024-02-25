# This file is used to mine private tracks and big artists from SoundCloud
# Sometimes, the program will be blocked by SoundCloud, so you need to change your IP address to continue mining
from lib.load_settings import load_settings, print_settings
from lib.get_log_dir import get_log_dir
from lib.username import val_username
import random
import string
import aiohttp
import asyncio
import aiofiles
import re
import os

# vars
SETTINGS = {}
USERNAME = ""

# Create logs directory if it doesn't exist
os.makedirs(get_log_dir(), exist_ok=True)


# Enum of URL types
class URLType:
    # small private track
    PRIVATE_SMALL_ARTIST = "private_small_artist"
    # private track with more than 1000 followers
    PRIVATE_BIG_ARTIST = "private_big_artist"
    # small playcount track in public
    PUBLIC_SMALL_PLAYCOUNT = "public_small_playcount"
    # big playcount track in publicJJ:W
    PUBLIC_BIG_PLAYCOUNT = "public_big_playcount"


# Asynchronous function to save URL
async def save_url(url: str, url_type: URLType):
    filename = {
        URLType.PRIVATE_SMALL_ARTIST: SETTINGS["PRIVATE_SMALL_ARTIST_URLS_FILENAME"],
        URLType.PRIVATE_BIG_ARTIST: SETTINGS["PRIVATE_BIG_ARTIST_URLS_FILENAME"],
        URLType.PUBLIC_SMALL_PLAYCOUNT: SETTINGS[
            "PUBLIC_SMALL_PLAYCOUNT_URLS_FILENAME"
        ],
        URLType.PUBLIC_BIG_PLAYCOUNT: SETTINGS["PUBLIC_BIG_PLAYCOUNT_URLS_FILENAME"],
    }[url_type]
    async with aiofiles.open(os.path.join(get_log_dir(), filename), "a") as f:
        await f.write(url + "\n")


# Function to generate a random link
def gen_link():
    base_url = "https://on.soundcloud.com/"
    random_id = "".join(random.choices(string.ascii_letters + string.digits, k=5))
    return base_url + random_id


# Asynchronous function to get a random URL
async def get_random_url(session):
    while True:
        url = gen_link()
        print(f"validating {url}")
        async with session.post(
            "https://soundcloud.com/oembed", data={"format": "json", "url": url}
        ) as response:
            if response.status == 200:
                return url
            if response.status == 403:
                print("possibly banned, waiting 120 seconds")
                await asyncio.sleep(120)


async def get_playcount(html_content: str) -> int:
    match = re.search(r'"playback_count":(\d+)', html_content)
    if match:
        return int(match.group(1))
    return -1


# Function to check if the link is private
async def is_private_producer(html_content: str) -> bool:
    match = re.search(r'"sharing":\s*"(\w+)"', html_content)
    if match:
        sharing = match.group(1)
        return sharing == "private"
    return False


async def artist_follower_count(html_content: str) -> int:
    match = re.search(r'"followers_count":(\d+)', html_content)
    if match:
        return int(match.group(1))
    return 0


async def get_artist_name(html_content: str) -> str:
    match = re.search(r'"username":"([^"]+)"', html_content)
    if match:
        return match.group(1)
    return "unknown"


# Asynchronous function to filter URL
async def filter_url(session, n_url):
    async with session.get(n_url) as response:
        if response.status != 200:
            return {"url": URLType.PUBLIC_BIG_PLAYCOUNT}, True
        html_content = await response.text()
        playcount: int = await get_playcount(html_content)
        is_small_playcount: bool = (
            playcount < SETTINGS["PUBLIC_SMALL_PLAYCOUNT_THRESHOLD"]
        )
        is_private = await is_private_producer(html_content)
        artist_follower_count_d = await artist_follower_count(html_content)
        is_artist_big = (
            artist_follower_count_d > SETTINGS["PRIVATE_BIG_ARTIST_THRESHOLD"]
        )
        if is_private:
            if is_artist_big:
                artist_name = await get_artist_name(html_content)
                return {
                    "url": URLType.PRIVATE_BIG_ARTIST,
                    "artist_name": artist_name,
                    "follower_count": artist_follower_count_d,
                }, False
            return {"url": URLType.PRIVATE_SMALL_ARTIST}, False
        if is_small_playcount:
            return {"url": URLType.PUBLIC_SMALL_PLAYCOUNT}, False
        return {"url": URLType.PUBLIC_BIG_PLAYCOUNT}, False


# Asynchronous function to notify
async def ntfy(session, private_url, follower_count, artist_name):
    database_url = SETTINGS["DATA_SERVER_URL"]
    data = {
        "url": private_url,
        "sender_name": USERNAME,
        "follower_count": follower_count,
        "artist_name": artist_name,
    }
    print(str(data))
    await session.post(f"{database_url}/url", json=data)


async def main():
    semaphore = asyncio.Semaphore(SETTINGS["CONCURRENT_TASKS"])
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(bounded_random_url(semaphore, session))
            for _ in range(SETTINGS["CONCURRENT_TASKS"])
        ]
        await asyncio.gather(*tasks)


async def bounded_random_url(semaphore, session):
    while True:  # Keep running indefinitely
        async with semaphore:
            random_url = await get_random_url(session)
            data_obj, err = await filter_url(
                session, random_url
            )  # Make sure to use the correct function name
            url_type = data_obj["url"]
            print(f"URL: {random_url}, Type: {url_type}")
            if not err:
                await save_url(
                    random_url, url_type
                )  # Await the async save_url function
            if url_type == URLType.PRIVATE_BIG_ARTIST:
                print(f"sending to server...")
                follower_count = data_obj["follower_count"]
                artist_name = data_obj["artist_name"]
                await ntfy(session, random_url, follower_count, artist_name)


if __name__ == "__main__":
    SETTINGS = load_settings()
    print_settings(SETTINGS)
    USERNAME = val_username()

    asyncio.run(main())
