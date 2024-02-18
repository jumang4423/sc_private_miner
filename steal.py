import random
import string
import requests
from typing import Union
import re
import os

# env_vars
PRIVATE_URLS_FILENAME = 'private_urls.txt'
SMALL_PLAYCOUNT_FILENAME = 'small_playcount.txt'
SMALL_PLAYCOUNT_THRESHOLD = 50000
NORMAL_URLS_FILENAME = 'normal_urls.txt'


# enum of private, small playcount, and normal
class URLType:
    PRIVATE = "private"
    SMALL_PLAYCOUNT = "small_playcount"
    NORMAL = "normal"

# create logs directory
LOG_DIR = 'logs'
try:
    os.mkdir(LOG_DIR)
except FileExistsError:
    pass

def save_url(url: str, url_type: URLType):
    print(f"saving with type: {url_type}")
    if url_type == URLType.PRIVATE:
        with open(LOG_DIR + '/' + PRIVATE_URLS_FILENAME, 'a') as f:
            f.write(url + '\n')
    elif url_type == URLType.SMALL_PLAYCOUNT:
        with open(LOG_DIR + '/' + SMALL_PLAYCOUNT_FILENAME, 'a') as f:
            f.write(url + '\n')
    else:
        with open(LOG_DIR + '/' + NORMAL_URLS_FILENAME, 'a') as f:
            f.write(url + '\n')



def gen_link():
    base_url = 'https://on.soundcloud.com/'
    random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return base_url + random_id

def get_random_url():
    while True:
        url = gen_link()
        print(f"validating url: {url}")
        response = requests.post('https://soundcloud.com/oembed', data={'format': 'json', 'url': url})
        
        if response.status_code == 200:
            return url

def is_tiny_producer(html_content: str) -> bool:
    """
    Check if the producer is a tiny producer based on SMALL_PLAYCOUNT_THRESHOLD
    """
    match = re.search(r'"playback_count":(\d+)', html_content)
    if match:
        this_playcount = int(match.group(1))
        print(f"playcount: {this_playcount}")
        return this_playcount < SMALL_PLAYCOUNT_THRESHOLD
    return False

def is_private_producer(html_content: str) -> bool:
    """
    Check if the sc link is private
    """
    match = re.search(r'"sharing":\s*"(\w+)"', html_content)
    if match:
        sharing = match.group(1)
        print(f"sharing: {sharing}")
        return sharing == 'private'
    return False


def filter(n_url) -> Union[URLType, bool]:
    """
    Filter the url based on the following criteria:
    - private
    - small playcount
    - normal
    """
    response = requests.get(n_url)
    if response.status_code != 200:
        return URLType.NORMAL, True
    # parse the html
    html_content = response.text
    is_small_playcount = is_tiny_producer(html_content)
    is_private = is_private_producer(html_content)
    if is_private:
        return URLType.PRIVATE, False   
    if is_small_playcount:
        return URLType.SMALL_PLAYCOUNT, False
    
    return URLType.NORMAL, False

def ntfy(private_url):
    requests.post('https://ntfy.sh/sc_private_miner', data=f"new private url: {private_url}".encode('utf-8'))

def main():
    while True:
        random_url = get_random_url()
        url_type, err = filter(random_url)
        if not err:
            save_url(random_url, url_type)
        if url_type == URLType.PRIVATE:
            # if new private url, notify to the ntfy.sh
            ntfy(random_url)

if __name__ == '__main__':
    main()