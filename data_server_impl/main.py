import os
import random
from pydantic import BaseModel
from datetime import datetime
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

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


class PrivateURL(PrivateURLDTO):
    timestamp: datetime


# Firestore Service
class FirestoreService:
    @staticmethod
    def get_random_private_url():
        """
        TODO: maybe this is very slow and inefficient
        """
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

    @staticmethod
    def get_urls(page_size, cursor=None, desc_key=None):
        if not desc_key:
            desc_key = "timestamp"
        urls_ref = db.collection("urls").order_by(
            desc_key, direction=firestore.Query.DESCENDING
        )
        # Use cursor-based pagination
        if cursor:
            cursor_doc = db.collection("urls").document(cursor).get()
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
    def add_url(url_data):
        url_data["timestamp"] = datetime.now()
        new_data = PrivateURL(**url_data)
        db.collection("urls").add(new_data.dict())


# Flask Routes
@app.route("/random_private_url", methods=["GET"])
def get_random_private_url():
    return FirestoreService.get_random_private_url()


@app.route("/urls", methods=["GET"])
def get_urls():
    try:
        page_size = int(request.args.get("page_size", 10))
        cursor = request.args.get("cursor", None)  # Get the cursor if provided
        desc_key = request.args.get("desc_key", None) # Get the desc_key if provided
        urls, next_cursor = FirestoreService.get_urls(page_size, cursor, desc_key)

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
        FirestoreService.add_url(data)
        return {"message": "URL added successfully"}, 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
