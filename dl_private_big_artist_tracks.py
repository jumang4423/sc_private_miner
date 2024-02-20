# this file download private tracks of big artists from SoundCloud
from lib.load_settings import load_settings, print_settings
from lib.get_log_dir import get_log_dir
import youtube_dl
import requests
import os
import re

# vars
SETTINGS = {}

class Metadata:
    id: str
    name: str
    artist: str
    playcount: int
    followers: int

# Create logs directory if it doesn't exist
os.makedirs(get_log_dir(), exist_ok=True)


def load_urls(filename: str):
    """
    Load URLs from file
    """
    list_of_urls = []
    with open(os.path.join(get_log_dir(), filename), 'r') as f:
        for line in f:
            if 'on.soundcloud.com' in line:
                list_of_urls.append(line.strip())
    
    return list_of_urls

def print_urls(list_of_urls):
    """
    Print URLs to console
    """
    for i, url in enumerate(list_of_urls):
        print(f"{i+1}: {url}")

def get_id_from_url(url: str):
    """
    Get ID from URL
    """
    return url.split('/')[-1]

def load_metadata_from_url(url: str) -> Metadata:
    """
    Load metadata from URL
    """
    metadata = Metadata()
    metadata.id = get_id_from_url(url)
    response = requests.get(url)
    resp_html = response.text
    # TODO: parse HTML to get metadata




def start_download(list_of_urls):
    """
    Start download
    """
    for i, url in enumerate(list_of_urls):
        print(f"Downloading {i+1}/{len(list_of_urls)}: {url}")
        this_id = get_id_from_url(url)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(get_log_dir(), 'private_big_artist_tracks', f"{this_id}.mp3"),
            'quiet': False,
            'no_warnings': False,
            'no_color': False,
            'noplaylist': True,
            'ignoreerrors': True,
            'nooverwrites': True,
            'writethumbnail': False,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

if __name__ == '__main__':
    SETTINGS = load_settings()
    print_settings(SETTINGS)
    list_of_urls = load_urls(SETTINGS['PRIVATE_BIG_ARTIST_URLS_FILENAME'])
    print(f"Loaded {len(list_of_urls)} URLs")
    print_urls(list_of_urls)
    yn = input("Do you want to download all of these URLs? (y/n) ")
    if yn == 'y':
        start_download(list_of_urls)