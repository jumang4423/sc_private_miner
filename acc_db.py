from lib.load_settings import load_settings, print_settings
import requests

# vars
SETTINGS = {}
PAGE_SIZE = 5


def get_page(cursor):
    global PAGE_SIZE, SETTINGS
    response = requests.get(
        f"{SETTINGS['DATA_SERVER_URL']}/urls",
        params={"cursor": cursor, "page_size": PAGE_SIZE},
    )
    return response.json().get("urls", []), response.json().get("next_cursor", None)


def print_url(da):
    print("*" * 20)
    print(f"url:          {da['url']}")
    print(f"-- artist_name:  {da['artist_name']}")
    print(f"-- follower_cnt: {da['follower_count']}")
    print(f"-- sender_name:  {da['sender_name']}")
    print(f"-- timestamp:    {da['timestamp']}")


def get_db_list():
    cur_cursor = None

    while True:
        new_page, cursor = get_page(cur_cursor)
        if len(new_page) == 0:
            print("no page found")
            break
        for d in new_page:
            print_url(d)
            print()
        input("enter to next page")
        print("-" * 80)
        cur_cursor = cursor


def get_random_private_url():
    response = requests.get(
        f"{SETTINGS['DATA_SERVER_URL']}/random_private_url",
    )
    return response.json()["url"]


if __name__ == "__main__":
    SETTINGS = load_settings()
    print_settings(SETTINGS)

    ans = input("(l)get_db_list, (r)get_random_private_url: ")
    if ans == "l":
        get_db_list()
    elif ans == "r":
        print(get_random_private_url())
    else:
        print("huh?")
