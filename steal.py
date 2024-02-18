import random
import string
import aiohttp
import asyncio
from typing import Union
import aiofiles
import re
import os

# Constants and environment variables
PRIVATE_URLS_FILENAME = 'private_urls.txt'
SMALL_PLAYCOUNT_FILENAME = 'small_playcount.txt'
SMALL_PLAYCOUNT_THRESHOLD = 50000
NORMAL_URLS_FILENAME = 'normal_urls.txt'
LOG_DIR = 'logs'
CONCURRENT_TASKS = 1

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Enum of URL types
class URLType:
    PRIVATE = "private"
    SMALL_PLAYCOUNT = "small_playcount"
    NORMAL = "normal"

# Asynchronous function to save URL
async def save_url(url: str, url_type: URLType):
    filename = {
        URLType.PRIVATE: PRIVATE_URLS_FILENAME,
        URLType.SMALL_PLAYCOUNT: SMALL_PLAYCOUNT_FILENAME,
        URLType.NORMAL: NORMAL_URLS_FILENAME
    }[url_type]
    async with aiofiles.open(os.path.join(LOG_DIR, filename), 'a') as f:
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
                print("possibly banned, waiting 10 seconds")
                await asyncio.sleep(10)

# Function to check if the producer is a tiny producer
async def is_tiny_producer(html_content: str) -> bool:
    match = re.search(r'"playback_count":(\d+)', html_content)
    if match:
        this_playcount = int(match.group(1))
        return this_playcount < SMALL_PLAYCOUNT_THRESHOLD
    return False

# Function to check if the link is private
async def is_private_producer(html_content: str) -> bool:
    match = re.search(r'"sharing":\s*"(\w+)"', html_content)
    if match:
        sharing = match.group(1)
        return sharing == 'private'
    return False

# Asynchronous function to filter URL
async def filter_url(session, n_url) -> Union[URLType, bool]:
    async with session.get(n_url) as response:
        if response.status != 200:
            return URLType.NORMAL, True
        html_content = await response.text()
        is_small_playcount = await is_tiny_producer(html_content)
        is_private = await is_private_producer(html_content)
        if is_private:
            return URLType.PRIVATE, False
        if is_small_playcount:
            return URLType.SMALL_PLAYCOUNT, False
        return URLType.NORMAL, False

# Asynchronous function to notify
async def ntfy(session, private_url):
    await session.post('https://ntfy.sh/sc_private_miner_ntfy', data=f"new private url: {private_url}".encode('utf-8'))


async def main():
    semaphore = asyncio.Semaphore(CONCURRENT_TASKS)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(bounded_random_url(semaphore, session)) for _ in range(5)]
        await asyncio.gather(*tasks)

async def bounded_random_url(semaphore, session):
    while True:  # Keep running indefinitely
        async with semaphore:
            random_url = await get_random_url(session)
            url_type, err = await filter_url(session, random_url)  # Make sure to use the correct function name
            print(f"URL: {random_url}, Type: {url_type}")
            if not err:
                await save_url(random_url, url_type)  # Await the async save_url function
            if url_type == URLType.PRIVATE:
                await ntfy(session, random_url)  # Await the async ntfy function

if __name__ == '__main__':
    print("sc_private_miner v0.1")
    print("- local mode: 0")
    print("- server mode: 1")
    print("choose: ", end="")
    mode = int(input())
    if mode == 0:
        CONCURRENT_TASKS = 1
    elif mode == 1:
        CONCURRENT_TASKS = 10

    asyncio.run(main())