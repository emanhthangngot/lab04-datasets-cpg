# Spark Metadata Streaming

Run this job inside the Spark container:

```bash
docker compose exec spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /app/spark_jobs/metadata_stream_to_mongo.py
```

Verified behavior:

- The Kafka package version matches the Spark 3.5.0 container.
- Accepted checkpoint evidence is stored for `/mnt/checkpoints/cpg_metadata`.
- Stage 3 proves MongoDB replacement/upsert by `file_id` during replay.
