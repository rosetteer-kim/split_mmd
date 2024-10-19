from pymongo import MongoClient
from bson import ObjectId
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()
mongodb_uri = os.getenv('MONGODB_URI')

@contextmanager
def get_mongo_collection():
    client = MongoClient('mongodb://localhost:27017')
    # client = MongoClient(mongodb_uri)
    try:
        db = client.test_database
        yield db.test_mmd
    finally:
        client.close()

# Create
def create_document(document):
    with get_mongo_collection() as collection:
        result = collection.insert_one(document)
        print(f"Created document with id: {result.inserted_id}")
        return result.inserted_id
