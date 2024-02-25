import os

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

@app.route("/urls", methods=["GET"])
def get_urls():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    total_docs = db.collection("urls").stream()
    total_docs_count = sum(1 for _ in total_docs)
    last_document_to_retrieve = total_docs_count - (page - 1) * page_size
    if last_document_to_retrieve < 0:
        return jsonify({"urls": []}), 404
    first_document_to_retrieve = max(last_document_to_retrieve - page_size, 0)
    urls_ref = db.collection("urls").order_by('timestamp', direction=firestore.Query.DESCENDING).limit(page_size).offset(first_document_to_retrieve)
    urls = [url.to_dict() for url in urls_ref.stream()]
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