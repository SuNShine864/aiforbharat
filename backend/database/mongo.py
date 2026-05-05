from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["tender_ai_db"]

tender_collection = db["tenders"]
bidder_collection = db["bidders"]