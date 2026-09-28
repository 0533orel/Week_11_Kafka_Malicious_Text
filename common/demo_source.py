"""Synthetic offline source; labels exercise routing, not claims about people."""
import json
import os
from pathlib import Path


def source_uri():
    if os.getenv("SOURCE_MODE", "demo") != "mongo":
        raise ValueError("SOURCE_MODE must be demo or mongo")
    uri = os.getenv("ATLAS_URI", "").strip()
    if not uri:
        raise ValueError("ATLAS_URI must be set in mongo mode")
    return uri


def load_demo():
    return json.loads(Path(__file__).with_name("demo_messages.json").read_text(encoding="utf-8"))


def publish_demo(producer, messages, positive_topic, negative_topic):
    for message in messages:
        topic = positive_topic if message["antisemietic"] else negative_topic
        producer.send(topic, message).get(timeout=30)
    producer.flush()


if __name__ == "__main__":
    print(json.dumps(load_demo(), indent=2))
