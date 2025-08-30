# Malicious Text Feature Engineering System (Minimal, Clean, Python)

A small, readable implementation of the assignment pipeline using **Kafka**, **MongoDB**, and simple Python.
No heavy NLP libraries. Clean, standard code — just enough to satisfy the spec.

## Services

1. **retriever**: Fetches documents from MongoDB Atlas in chronological order (oldest first), 100 per minute,
   and publishes to Kafka topics:
   - `raw_tweets_antisemitic`
   - `raw_tweets_not_antisemitic`

2. **preprocessor**: Subscribes to both raw topics, cleans text (punctuation/specials/whitespace/stopwords, lowercase,
   light lemmatization) and republishes to:
   - `preprocessed_tweets_antisemitic`
   - `preprocessed_tweets_not_antisemitic`

3. **enricher**: Subscribes to both preprocessed topics, adds:
   - `sentiment` (simple lexicon-based: positive/negative/neutral)
   - `weapons_detected` (list from blacklist)
   - `relevant_timestamp` (latest date in content, if any)
   Publishes to:
   - `enriched_preprocessed_tweets_antisemitic`
   - `enriched_preprocessed_tweets_not_antisemitic`

4. **persister**: Subscribes to both enriched topics and saves to **local MongoDB** collections:
   - `tweets_antisemitic`
   - `tweets_not_antisemitic`
   (The saved schema matches the assignment.)

5. **dataretrieval**: Simple FastAPI with two endpoints:
   - `GET /antisemitic?limit=100`
   - `GET /not_antisemitic?limit=100`


## Quick Start (Local, with Docker)

1. Copy the environment template:
   ```bash
   cp config/.env.example config/.env
   ```

2. Start infra (Kafka+Zookeeper+Mongo):
   ```bash
   docker compose up -d zookeeper kafka mongo
   ```

3. Create topics (run once — see `scripts/kafka_local_cli.txt` for details). Example:
   ```bash
   bash scripts/kafka_local_cli.txt
   ```

4. Build and run all services:
   ```bash
   docker compose up -d --build retriever preprocessor enricher persister dataretrieval
   ```

5. Test API:
   - Antisemitic:  `http://localhost:8000/antisemitic?limit=50`
   - Not antisemitic: `http://localhost:8000/not_antisemitic?limit=50`


## Local Development (without Docker)

- Each service can be run with `python app.py`. Set env vars from `.env` manually (or export them).
- See `scripts/services_cli.txt` for useful one-liners.


## Notes

- Minimal dependencies: `kafka-python`, `pymongo`, and `fastapi/uvicorn` (for the API).
- Light lemmatization and stopwords implemented by hand (tiny, readable). No heavy NLP libs.
- Weapons blacklist in `services/enricher/weapons_blacklist.txt` — extend as you wish.
- Retriever keeps progress in `/data/retriever_state.json` (bind-mounted volume in compose).


## OpenShift (Bonus)

- See `scripts/openshift_commands.bat` and `scripts/openshift/*.yaml` for a starting point.
- These are minimal examples; you may need to adjust envs and image names.
