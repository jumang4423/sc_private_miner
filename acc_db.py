from lib.load_settings import load_settings, print_settings
from datetime import datetime
import requests
import time
from datetime import datetime, timezone, timedelta

# vars
SETTINGS = {}
PAGE_SIZE = 5


def get_page(cursor, desc_key, is_small):
    global PAGE_SIZE, SETTINGS
    response = requests.get(
        f"{SETTINGS['DATA_SERVER_URL']}/urls",
        params={
            "cursor": cursor, 
            "page_size": PAGE_SIZE,
            "desc_key": desc_key,
            "is_small": is_small,
        },
    )
    return response.json().get("urls", []), response.json().get("next_cursor", None)


def translate_local_time(gmt_time: str):
    dt_gmt = datetime.strptime(gmt_time, "%a, %d %b %Y %H:%M:%S %Z")
    dt_utc = dt_gmt.replace(tzinfo=timezone.utc)
    local_offset = timedelta(seconds=-time.timezone)
    if time.daylight:
        local_offset = timedelta(seconds=-time.altzone)
    local_timezone = timezone(local_offset)
    dt_local = dt_utc.astimezone(local_timezone)
    return dt_local.strftime("%Y-%m-%d %H:%M:%S")


def print_url(da):
    print("*" * 20)
    print(f"url:          {da['url']}")
    print(f"-- title:        {da.get('title', '-')}")
    print(f"-- artist_name:  {da['artist_name']}")
    print(f"-- follower_cnt: {da['follower_count']}")
    print(f"-- sender_name:  {da['sender_name']}")
    print(f"-- timestamp:    {translate_local_time(da['timestamp'])}")


def get_db_list(desc_key, is_small):
    cur_cursor = None

    while True:
        new_page, cursor = get_page(cur_cursor, desc_key, is_small)
        if len(new_page) == 0:
            print("no page found")
            break
        for d in new_page:
            print_url(d)
            print()
        input("enter to next page")
        print("-" * 80)
        cur_cursor = cursor


def get_random_private_url(is_small):
    response = requests.get(
        f"{SETTINGS['DATA_SERVER_URL']}/random_private_url",
        params={
            "is_small": is_small,
        },
    )
    return response.json()


if __name__ == "__main__":
    SETTINGS = load_settings()
    print_settings(SETTINGS)

    ans = input("(l)get_db_list, (r)get_random_private_url: ")
    if ans == "l":
        ans2 = input("sort by... (t)imestamp, (f)ollower_count: ")
        desc_key = ""
        if ans2 == "t":
            desc_key = "timestamp"
        elif ans2 == "f":
            desc_key = "follower_count"
        else:
            print("huh?")
            exit()
        ans3 = input("artist size? (b)ig, (s)mall: ")
        is_small = False
        if ans3 == "b":
            is_small = False
        elif ans3 == "s":
            is_small = True
        else:
            print("huh?")
            exit()
        get_db_list(desc_key, is_small)
    elif ans == "r":
        ans2 = input("artist size? (b)ig, (s)mall: ")
        is_small = False
        if ans2 == "b":
            is_small = False
        elif ans2 == "s":
            is_small = True
        else:
            print("huh?")
            exit()
        print_url(get_random_private_url(is_small))
    else:
        print("huh?")
