import os
from typing import List
from fastapi import FastAPI, Query
from pymongo import MongoClient

API_BIND = os.getenv("API_BIND","0.0.0.0")
API_PORT = int(os.getenv("API_PORT","8000"))

MONGO_LOCAL_URI = os.getenv("MONGO_LOCAL_URI", "mongodb://mongo:27017")
MONGO_LOCAL_DB = os.getenv("MONGO_LOCAL_DB", "localdb")

COLL_ANT = "tweets_antisemitic"
COLL_NOT = "tweets_not_antisemitic"

app = FastAPI(title="DataRetrieval", version="1.0")

mongo = MongoClient(MONGO_LOCAL_URI)
db = mongo[MONGO_LOCAL_DB]

@app.get("/antisemitic")
def get_antisemitic(limit: int = Query(100, ge=1, le=1000)):
    cur = db[COLL_ANT].find().sort("createdate", -1).limit(limit)
    return [normalize(doc) for doc in cur]

@app.get("/not_antisemitic")
def get_not_antisemitic(limit: int = Query(100, ge=1, le=1000)):
    cur = db[COLL_NOT].find().sort("createdate", -1).limit(limit)
    return [normalize(doc) for doc in cur]

def normalize(doc):
    doc["_id"] = str(doc.get("_id"))
    if doc.get("createdate"):
        doc["createdate"] = doc["createdate"].isoformat()
    return doc

# Docker runs uvicorn via CMD in Dockerfile
