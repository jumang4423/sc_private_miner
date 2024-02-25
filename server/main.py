import os
import random
from pydantic import BaseModel
from datetime import datetime
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

CRED_PATH = "./credentials.json"
cred = credentials.Certificate(CRED_PATH)
initialize_app(cred)
db = firestore.client()

app = Flask(__name__)


class PrivateURLDTO(BaseModel):
    url: str
    sender_name: str
    follower_count: int
    artist_name: str


class PrivateURL(PrivateURLDTO):
    timestamp: datetime


@app.route("/random_private_url", methods=["GET"])
def get_random_private_url():
    try:
        urls_ref = db.collection("urls")
        urls_stream = urls_ref.stream()
        total_docs_count = sum(1 for _ in urls_stream)
        if total_docs_count == 0:
            return jsonify({"error": "No URLs found"}), 404
        random_index = random.randint(0, total_docs_count - 1)
        random_doc_ref = (
            urls_ref.order_by("timestamp").offset(random_index).limit(1).stream()
        )
        random_doc = next(random_doc_ref, None)
        if random_doc:
            return jsonify(random_doc.to_dict()), 200
        else:
            return jsonify({"error": "Random URL not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/urls", methods=["GET"])
def get_urls():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    urls_ref = db.collection("urls").order_by(
        "timestamp", direction=firestore.Query.DESCENDING
    )

    skip = (page - 1) * page_size

    if skip:
        last_doc_of_previous_page = urls_ref.limit(skip).stream()
        last_docs = list(last_doc_of_previous_page)
        if last_docs:
            last_doc = last_docs[-1]
            urls_ref = urls_ref.start_after(last_doc)

    urls = [url.to_dict() for url in urls_ref.limit(page_size).stream()]

    if not urls:
        return jsonify({"urls": []}), 404

    return jsonify({"urls": urls})


@app.route("/url", methods=["POST"])
# add url to urls collection
def add_url():
    data = request.json
    url = PrivateURLDTO(**data).dict()
    url["timestamp"] = datetime.now()
    # validate url
    new_data = PrivateURL(**url)
    db.collection("urls").add(new_data.dict())
    return {"message": "URL added successfully"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
