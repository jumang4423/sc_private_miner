# This file is used to mine private tracks and big artists from SoundCloud
# Sometimes, the program will be blocked by SoundCloud, so you need to change your IP address to continue mining
from lib.load_settings import load_settings, print_settings
from lib.get_log_dir import get_log_dir
from typing import Union
import random
import string
import aiohttp
import asyncio
import aiofiles
import re
import os

# vars
SETTINGS = {}

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
        URLType.PRIVATE_SMALL_ARTIST: SETTINGS['PRIVATE_SMALL_ARTIST_URLS_FILENAME'],
        URLType.PRIVATE_BIG_ARTIST: SETTINGS['PRIVATE_BIG_ARTIST_URLS_FILENAME'],
        URLType.PUBLIC_SMALL_PLAYCOUNT: SETTINGS['PUBLIC_SMALL_PLAYCOUNT_URLS_FILENAME'],
        URLType.PUBLIC_BIG_PLAYCOUNT: SETTINGS['PUBLIC_BIG_PLAYCOUNT_URLS_FILENAME']
    }[url_type]
    async with aiofiles.open(os.path.join(get_log_dir(), filename), 'a') as f:
        await f.write(url + '\n')

# Function to generate a random link
def gen_link():
    base_url = 'https://on.soundcloud.com/'
    random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return base_url + random_id

# Asynchronous function to get a random URL
async def get_random_url(session):
    while True:
        url = gen_link()
        print(f"validating {url}")
        async with session.post('https://soundcloud.com/oembed', data={'format': 'json', 'url': url}) as response:
            if response.status == 200:
                return url
            if response.status == 403:
                print("possibly banned, waiting 60 seconds")
                await asyncio.sleep(60)

# Function to check if the producer is a tiny producer
async def is_tiny_producer(html_content: str) -> bool:
    match = re.search(r'"playback_count":(\d+)', html_content)
    if match:
        this_playcount = int(match.group(1))
        return this_playcount < SETTINGS['PUBLIC_SMALL_PLAYCOUNT_THRESHOLD']
    return False

# Function to check if the link is private
async def is_private_producer(html_content: str) -> bool:
    match = re.search(r'"sharing":\s*"(\w+)"', html_content)
    if match:
        sharing = match.group(1)
        return sharing == 'private'
    return False

async def is_big_artist(html_content: str) -> bool:
    match = re.search(r'"followers_count":(\d+)', html_content)
    if match:
        followers_count = int(match.group(1))
        return followers_count > SETTINGS['PRIVATE_BIG_ARTIST_THRESHOLD']
    return False

# Asynchronous function to filter URL
async def filter_url(session, n_url) -> Union[URLType, bool]:
    async with session.get(n_url) as response:
        if response.status != 200:
            return URLType.PUBLIC_BIG_PLAYCOUNT, True
        html_content = await response.text()
        is_small_playcount = await is_tiny_producer(html_content)
        is_private = await is_private_producer(html_content)
        if is_private:
            if await is_big_artist(html_content):
                return URLType.PRIVATE_BIG_ARTIST, False
            return URLType.PRIVATE_SMALL_ARTIST, False
        if is_small_playcount:
            return URLType.PUBLIC_SMALL_PLAYCOUNT, False
        return URLType.PUBLIC_BIG_PLAYCOUNT, False

# Asynchronous function to notify
async def ntfy(session, private_url):
    await session.post('https://ntfy.sh/sc_private_miner_ntfy', data=f"new private url: {private_url}".encode('utf-8'))


async def main():
    semaphore = asyncio.Semaphore(SETTINGS['CONCURRENT_TASKS'])
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(bounded_random_url(semaphore, session)) for _ in range(SETTINGS['CONCURRENT_TASKS'])]
        await asyncio.gather(*tasks)

async def bounded_random_url(semaphore, session):
    while True:  # Keep running indefinitely
        async with semaphore:
            random_url = await get_random_url(session)
            url_type, err = await filter_url(session, random_url)  # Make sure to use the correct function name
            print(f"URL: {random_url}, Type: {url_type}")
            if not err:
                await save_url(random_url, url_type)  # Await the async save_url function
            if url_type == URLType.PRIVATE_SMALL_ARTIST or url_type == URLType.PRIVATE_BIG_ARTIST:
                if SETTINGS['IS_NTFY']:
                    await ntfy(session, random_url)  # Await the async ntfy function


if __name__ == '__main__':
    SETTINGS = load_settings()
    print_settings(SETTINGS)
    asyncio.run(main())