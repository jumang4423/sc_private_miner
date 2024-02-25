from lib.load_settings import load_settings, print_settings
import requests

# vars
SETTINGS = {}
PAGE_SIZE = 5


def get_page(cur_page: int):
    global PAGE_SIZE, SETTINGS
    response = requests.get(
        f"{SETTINGS['DATA_SERVER_URL']}/urls",
        params={"page": cur_page, "page_size": PAGE_SIZE},
    )
    return response


if __name__ == "__main__":
    SETTINGS = load_settings()
    print_settings(SETTINGS)
    cur_page = 1

    while True:
        new_page = get_page(cur_page)
        print(new_page)
        input("enter to next page")
        cur_page = cur_page + 1
