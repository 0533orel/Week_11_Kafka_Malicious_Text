import os, json
from kafka import KafkaConsumer, KafkaProducer
from common.sentiment import sentiment_from_text
from common.weapons import load_blacklist, detect_weapons
from common.time_utils import latest_timestamp_in_text

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

TOPIC_PREP_ANT = os.getenv("TOPIC_PREP_ANT", "preprocessed_tweets_antisemitic")
TOPIC_PREP_NOT = os.getenv("TOPIC_PREP_NOT", "preprocessed_tweets_not_antisemitic")

TOPIC_ENR_ANT = os.getenv("TOPIC_ENR_ANT", "enriched_preprocessed_tweets_antisemitic")
TOPIC_ENR_NOT = os.getenv("TOPIC_ENR_NOT", "enriched_preprocessed_tweets_not_antisemitic")

GROUP_ID = os.getenv("CONSUMER_GROUP", "enricher_group")
AUTO_RESET = os.getenv("AUTO_OFFSET_RESET", "earliest")
BLACKLIST_PATH = os.getenv("BLACKLIST_PATH", "/app/weapons_blacklist.txt")

def main():
    print("[enricher] loading blacklist...")
    bl = load_blacklist(BLACKLIST_PATH)

    print("[enricher] connecting to Kafka...")
    consumer = KafkaConsumer(
        TOPIC_PREP_ANT, TOPIC_PREP_NOT,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset=AUTO_RESET,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        retries=3,
        linger_ms=50
    )

    topics_map = {
        TOPIC_PREP_ANT: TOPIC_ENR_ANT,
        TOPIC_PREP_NOT: TOPIC_ENR_NOT
    }

    for msg in consumer:
        payload = msg.value
        clean_text = payload.get("clean_text", "")

        payload["sentiment"] = sentiment_from_text(clean_text)
        payload["weapons_detected"] = detect_weapons(clean_text, bl)
        payload["relevant_timestamp"] = latest_timestamp_in_text(payload.get("original_text",""))

        out_topic = topics_map.get(msg.topic, TOPIC_ENR_NOT)
        producer.send(out_topic, payload)
        producer.flush()

if __name__ == "__main__":
    main()
