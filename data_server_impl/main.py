import os
import random
import logging
# log set everything
logging.basicConfig(level=logging.INFO)
from pydantic import BaseModel
from datetime import datetime
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
from typing import Optional
# Initialize Firestore DB
CRED_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "./credentials.json")
cred = credentials.Certificate(CRED_PATH)
initialize_app(cred)
db = firestore.client()
app = Flask(__name__)


# DTO and Model
class PrivateURLDTO(BaseModel):
    url: str
    sender_name: str
    follower_count: int
    artist_name: str
    title: Optional[str] = None


class PrivateURL(PrivateURLDTO):
    timestamp: datetime


# Firestore Service
class FirestoreService:
    @staticmethod
    def get_random_private_url(is_small: bool):
        """
        TODO: maybe this is very slow and inefficient
        """
        try:
            col_refa = "urls"
            if is_small:
                col_refa = "small_urls"
            urls_ref = db.collection(col_refa)
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

    @staticmethod
    def get_urls(page_size, cursor=None, desc_key=None, is_small=False):
        col_ref = "urls"
        if is_small:
            col_ref = "small_urls"
        if not desc_key:
            desc_key = "timestamp"
        urls_ref = db.collection(col_ref).order_by(
            desc_key, direction=firestore.Query.DESCENDING
        )
        # Use cursor-based pagination
        if cursor:
            cursor_doc = db.collection(col_ref).document(cursor).get()
            if cursor_doc.exists:
                urls_ref = urls_ref.start_after(cursor_doc)

        query = urls_ref.limit(
            page_size + 1
        )  # Fetch one extra document to determine if there is a next page
        docs = list(query.stream())
        urls = [doc.to_dict() for doc in docs[:page_size]]

        next_cursor = None
        if len(docs) > page_size:  # Check if we fetched an extra document
            next_cursor = docs[page_size].id  # This is the cursor for the next page

        return urls, next_cursor

    @staticmethod
    def add_url(url_data, is_small):
        url_data["timestamp"] = datetime.now()
        new_data = PrivateURL(**url_data)
        collection_name = "urls"
        if is_small:
            collection_name = "small_urls"
        doc_ref = db.collection(collection_name).add(new_data.dict())

        return doc_ref.id


# Flask Routes
@app.route("/random_private_url", methods=["GET"])
def get_random_private_url():
    is_small = request.args.get("is_small", 0) == "1"
    return FirestoreService.get_random_private_url(is_small)


@app.route("/urls", methods=["GET"])
def get_urls():
    try:
        page_size = int(request.args.get("page_size", 10))
        cursor = request.args.get("cursor", None)  # Get the cursor if provided
        desc_key = request.args.get("desc_key", None) # Get the desc_key if provided
        is_small = request.args.get("is_small", 0) == "1"
        urls, next_cursor = FirestoreService.get_urls(page_size, cursor, desc_key, is_small)
        response = {"urls": urls}
        if next_cursor:
            response["next_cursor"] = next_cursor

        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"message": "Invalid page size"}), 400
    except Exception as e:
        return jsonify({"message": "An error occurred"}), 500


@app.route("/url", methods=["POST"])
def add_url():
    try:
        data = request.json
        new_doc_id = FirestoreService.add_url(data, False)
        return {"message": f"doc id: {new_doc_id}"}, 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/small_url", methods=["POST"])
def add_small_url():
    try:
        data = request.json
        new_doc_id = FirestoreService.add_url(data, True)
        return {"message": f"doc id: {new_doc_id}"}, 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
