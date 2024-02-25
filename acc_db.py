from lib.load_settings import load_settings, print_settings
import requests

# vars
SETTINGS = {}
PAGE_SIZE = 3


def get_page(cur_page: int):
    global PAGE_SIZE, SETTINGS
    response = requests.get(
        f"{SETTINGS['DATA_SERVER_URL']}/urls",
        params={"page": cur_page, "page_size": PAGE_SIZE},
    )
    return response.json()["urls"]


def print_url(da):
    print(f"url:          {da['url']}")
    print(f"-- artist_name:  {da['artist_name']}")
    print(f"-- follower_cnt: {da['follower_count']}")
    print(f"-- sender_name:  {da['sender_name']}")
    print(f"-- timestamp:    {da['timestamp']}")


def get_db_list():
    cur_page = 1

    while True:
        new_page = get_page(cur_page)
        if len(new_page) == 0:
            print("no page found")
            break
        for d in new_page:
            print_url(d)
            print()
        input("enter to next page")
        cur_page = cur_page + 1


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
