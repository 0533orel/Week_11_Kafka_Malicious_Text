import os, json, time
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from kafka import KafkaProducer
from bson import ObjectId

ATLAS_URI = os.getenv("ATLAS_URI", "mongodb+srv://IRGC_NEW:iran135@cluster0.6ycjkak.mongodb.net/")
ATLAS_DB = os.getenv("ATLAS_DB", "IranMalDB")
ATLAS_COLLECTION = os.getenv("ATLAS_COLLECTION", "texts")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC_RAW_ANT = os.getenv("TOPIC_RAW_ANT", "raw_tweets_antisemitic")
TOPIC_RAW_NOT = os.getenv("TOPIC_RAW_NOT", "raw_tweets_not_antisemitic")

STATE_PATH = os.getenv("STATE_PATH", "/data/retriever_state.json")  # mounted volume in compose
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", "60"))  # once per minute

def load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_createdate": None, "last_id": None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f)

def doc_createdate(doc):
    # handle possible field names, default to _id timestamp
    dt = doc.get("createdate") or doc.get("create_date") or None
    if isinstance(dt, datetime):
        return dt
    return doc.get("_id").generation_time if isinstance(doc.get("_id"), ObjectId) else None

def is_antisemitic(doc):
    # accept several spellings/fields
    for k in ["antisemietic","antisemitic","is_antisemitic","antisemitism_label","label"]:
        if k in doc:
            try:
                v = int(doc[k])
                return 1 if v else 0
            except Exception:
                return 1 if str(doc[k]).lower() in ("1","true","yes","y") else 0
    return 0

def main():
    print("[retriever] connecting to Atlas...")
    mongo = MongoClient(ATLAS_URI)
    col = mongo[ATLAS_DB][ATLAS_COLLECTION]

    print("[retriever] connecting to Kafka...")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        retries=5,
        linger_ms=50
    )

    state = load_state()
    print("[retriever] initial state:", state)

    while True:
        query = {}
        sort = [("createdate", ASCENDING)]
        if state.get("last_createdate"):
            query["createdate"] = {"$gt": datetime.fromisoformat(state["last_createdate"])}

        # Fallback: if no createdate field exists, just sort by _id
        sample = col.find_one()
        if sample and "createdate" not in sample:
            sort = [("_id", ASCENDING)]
            if state.get("last_id"):
                query["_id"] = {"$gt": ObjectId(state["last_id"])}

        cursor = col.find(query).sort(sort).limit(BATCH_SIZE)
        docs = list(cursor)
        if not docs:
            print("[retriever] no new docs. sleeping...")
            time.sleep(SLEEP_SECONDS)
            continue

        print(f"[retriever] fetched {len(docs)} docs")
        for d in docs:
            created = doc_createdate(d)
            ant = is_antisemitic(d)
            msg = {
                "id": str(d.get("_id")),
                "createdate": created.isoformat() if created else None,
                "antisemietic": ant,
                "original_text": d.get("text") or d.get("content") or d.get("original_text") or ""
            }
            topic = TOPIC_RAW_ANT if ant == 1 else TOPIC_RAW_NOT
            producer.send(topic, msg)

        producer.flush()

        # advance state
        last = docs[-1]
        state["last_createdate"] = doc_createdate(last).isoformat() if doc_createdate(last) else None
        state["last_id"] = str(last.get("_id")) if last.get("_id") else None
        save_state(state)

        print("[retriever] batch sent. sleeping...")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
