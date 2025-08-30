import os, json
from kafka import KafkaConsumer, KafkaProducer
from common.text_utils import clean_text

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

TOPIC_RAW_ANT = os.getenv("TOPIC_RAW_ANT", "raw_tweets_antisemitic")
TOPIC_RAW_NOT = os.getenv("TOPIC_RAW_NOT", "raw_tweets_not_antisemitic")

TOPIC_PREP_ANT = os.getenv("TOPIC_PREP_ANT", "preprocessed_tweets_antisemitic")
TOPIC_PREP_NOT = os.getenv("TOPIC_PREP_NOT", "preprocessed_tweets_not_antisemitic")

GROUP_ID = os.getenv("CONSUMER_GROUP", "preprocessor_group")
AUTO_RESET = os.getenv("AUTO_OFFSET_RESET", "earliest")

def main():
    print("[preprocessor] connecting to Kafka...")
    consumer = KafkaConsumer(
        TOPIC_RAW_ANT, TOPIC_RAW_NOT,
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
        TOPIC_RAW_ANT: TOPIC_PREP_ANT,
        TOPIC_RAW_NOT: TOPIC_PREP_NOT
    }

    for msg in consumer:
        payload = msg.value
        original = payload.get("original_text","")
        cleaned = clean_text(original)
        payload["clean_text"] = cleaned
        out_topic = topics_map.get(msg.topic, TOPIC_PREP_NOT)
        producer.send(out_topic, payload)
        producer.flush()

if __name__ == "__main__":
    main()
