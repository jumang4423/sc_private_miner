import os
import json
from firebase_admin import credentials, firestore, initialize_app
CRED_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "./credentials.json")
cred = credentials.Certificate(CRED_PATH)
initialize_app(cred)
db = firestore.client()

big_artist_json_path = "big_artist.json"
small_artist_json_path = "small_artist.json"

def get_all_urls(col_name: str) -> list:
    urls_ref = db.collection(col_name)
    urls_stream = urls_ref.stream()
    urls = [url.to_dict() for url in urls_stream]
    for url in urls:
        # timestamp to string because json doesn't support datetime
        url["timestamp"] = url["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return urls


# write to json
print("Writing to json...(0/2)")
with open(big_artist_json_path, "w") as f:
    json_data = {
        "urls": get_all_urls("urls")
    }
    json.dump(json_data, f, indent=4)
print("Writing to json...(1/2)")
with open(small_artist_json_path, "w") as f:
    json_data = {
        "urls": get_all_urls("small_urls")
    }
    json.dump(json_data, f, indent=4)

print("Done writing to json")