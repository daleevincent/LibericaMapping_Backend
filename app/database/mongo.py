from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo = None
db = None

def init_mongo(app):
    global mongo, db

    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)

    db = client[os.getenv("DB_NAME")]