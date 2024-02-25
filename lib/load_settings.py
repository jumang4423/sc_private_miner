import json

# Constants and env variables from json
SETTINGS_JSON_FILEPATH = "settings.json"


def load_settings():
    """
    Load settings from SETTINGS_JSON_FILEPATH
    """
    with open(SETTINGS_JSON_FILEPATH, "r") as f:
        settings = json.load(f)
        return settings


def print_settings(settings):
    """
    Print settings to console
    """
    print(
        f"PRIVATE_SMALL_ARTIST_URLS_FILENAME: {settings['PRIVATE_SMALL_ARTIST_URLS_FILENAME']}"
    )
    print(
        f"PRIVATE_BIG_ARTIST_URLS_FILENAME: {settings['PRIVATE_BIG_ARTIST_URLS_FILENAME']}"
    )
    print(
        f"PUBLIC_SMALL_PLAYCOUNT_URLS_FILENAME: {settings['PUBLIC_SMALL_PLAYCOUNT_URLS_FILENAME']}"
    )
    print(
        f"PUBLIC_BIG_PLAYCOUNT_URLS_FILENAME: {settings['PUBLIC_BIG_PLAYCOUNT_URLS_FILENAME']}"
    )
    print(
        f"PUBLIC_SMALL_PLAYCOUNT_THRESHOLD: {settings['PUBLIC_SMALL_PLAYCOUNT_THRESHOLD']}"
    )
    print(f"PRIVATE_BIG_ARTIST_THRESHOLD: {settings['PRIVATE_BIG_ARTIST_THRESHOLD']}")
    print(f"CONCURRENT_TASKS: {settings['CONCURRENT_TASKS']}")
    print(f"DATA_SERVER_URL: {settings['DATA_SERVER_URL']}")
    print(f"REQUEST_TIME_SEC: {settings['REQUEST_TIME_SEC']}")
