import os


def val_username():
    # check username file exists
    if not os.path.isfile(".username"):
        # if not, create one
        username = input("Enter your miner name: ")
        with open(".username", "w") as f:
            f.write(username)

    # read username from file
    with open(".username", "r") as f:
        return f.read().strip()
