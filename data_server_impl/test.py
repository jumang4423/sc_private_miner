import json

def sort_and_get_top_artists(data_file="big_artist.json"):
    """
    Sorts artists by follower_count and returns the top 10 in JSON format.

    Args:
        data_file (str, optional): The filename of the JSON data file. Defaults to "big_artist.json".
    """

    with open(data_file, 'r') as f:
        data = json.load(f)

    # Sort artists by follower_count (descending)
    sorted_artists = sorted(data['urls'], key=lambda item: item['follower_count'], reverse=True)

    # Get the top 10 artists
    top_10_artists = sorted_artists[:10]

    # Save top 10 artists to a new JSON file
    with open('top_10_artists.json', 'w') as f:
        json.dump(top_10_artists, f, indent=4)

    print("Top 10 artists saved to 'top_10_artists.json'")

# **Assuming your 'big_artist.json' file has the provided structure**
sort_and_get_top_artists() 