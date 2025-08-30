import os, json
from datetime import datetime
from kafka import KafkaConsumer
from pymongo import MongoClient

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

TOPIC_ENR_ANT = os.getenv("TOPIC_ENR_ANT", "enriched_preprocessed_tweets_antisemitic")
TOPIC_ENR_NOT = os.getenv("TOPIC_ENR_NOT", "enriched_preprocessed_tweets_not_antisemitic")

GROUP_ID = os.getenv("CONSUMER_GROUP", "persister_group")
AUTO_RESET = os.getenv("AUTO_OFFSET_RESET", "earliest")

MONGO_LOCAL_URI = os.getenv("MONGO_LOCAL_URI", "mongodb://mongo:27017")
MONGO_LOCAL_DB = os.getenv("MONGO_LOCAL_DB", "localdb")

COLL_ANT = "tweets_antisemitic"
COLL_NOT = "tweets_not_antisemitic"

def to_doc(payload: dict) -> dict:
    # Transform to the assignment's final schema
    # Guard against missing fields
    return {
        "id": payload.get("id"),
        "createdate": datetime.fromisoformat(payload["createdate"]) if payload.get("createdate") else None,
        "antisemietic": int(payload.get("antisemietic", 0)),
        "original_text": payload.get("original_text",""),
        "clean_text": payload.get("clean_text",""),
        "sentiment": payload.get("sentiment","neutral"),
        "weapons_detected": (payload.get("weapons_detected") or [""])[0] if isinstance(payload.get("weapons_detected"), list) else (payload.get("weapons_detected") or ""),
        "relevant_timestamp": payload.get("relevant_timestamp","")
    }

def main():
    print("[persister] connecting to Mongo local...")
    mongo = MongoClient(MONGO_LOCAL_URI)
    db = mongo[MONGO_LOCAL_DB]
    col_map = {
        TOPIC_ENR_ANT: db[COLL_ANT],
        TOPIC_ENR_NOT: db[COLL_NOT],
    }

    print("[persister] connecting to Kafka...")
    consumer = KafkaConsumer(
        TOPIC_ENR_ANT, TOPIC_ENR_NOT,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset=AUTO_RESET,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )

    for msg in consumer:
        payload = msg.value
        doc = to_doc(payload)
        target = col_map[msg.topic]
        target.insert_one(doc)
        print(f"[persister] saved to {target.name}: {doc.get('id')}")

if __name__ == "__main__":
    main()
