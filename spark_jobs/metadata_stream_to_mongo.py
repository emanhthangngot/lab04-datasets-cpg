"""Spark Structured Streaming job for Lab04 metadata ingestion.

Run inside the Spark container with both packages:
  docker compose exec spark spark-submit \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
    /app/spark_jobs/metadata_stream_to_mongo.py
"""

import signal
import sys

from pyspark.sql import SparkSession
from pyspark import StorageLevel
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import LongType, StringType, StructType

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
KAFKA_BOOTSTRAP = "broker:9092"
KAFKA_TOPIC = "cpg.metadata"
MONGO_URI = "mongodb://mongo:27017/"
MONGO_DATABASE = "cpg"
MONGO_COLLECTION = "file_metadata"
CHECKPOINT_PATH = "/mnt/checkpoints/cpg_metadata"
TRIGGER_INTERVAL = "10 seconds"

# ---------------------------------------------------------------------------
# Metadata event schema — must match parser_service/schemas.py
# ---------------------------------------------------------------------------
schema = (
    StructType()
    .add("schema_version", StringType())
    .add("event_time", StringType())
    .add("repo", StringType())
    .add("commit_sha", StringType())
    .add("run_id", StringType())
    .add("file_id", StringType())
    .add("file_path", StringType())
    .add("file_size", LongType())
    .add("content_hash", StringType())
    .add("num_ast_nodes", LongType())
    .add("num_cfg_edges", LongType())
    .add("num_dfg_edges", LongType())
    .add("num_call_edges", LongType())
    .add("num_total_edges", LongType())
    .add("parse_duration_ms", LongType())
    .add("status", StringType())
)

# ---------------------------------------------------------------------------
# Spark session
# ---------------------------------------------------------------------------
print("=" * 60)
print("CPG Metadata Ingestion — Spark Structured Streaming")
print("=" * 60)
print(f"  Kafka bootstrap : {KAFKA_BOOTSTRAP}")
print(f"  Kafka topic     : {KAFKA_TOPIC}")
print(f"  MongoDB URI     : {MONGO_URI}")
print(f"  MongoDB target  : {MONGO_DATABASE}.{MONGO_COLLECTION}")
print(f"  Checkpoint path : {CHECKPOINT_PATH}")
print(f"  Trigger interval: {TRIGGER_INTERVAL}")
print("=" * 60)

spark = (
    SparkSession.builder.appName("CPGMetadataIngestion")
    .config("spark.mongodb.write.connection.uri", MONGO_URI)
    .config("spark.mongodb.write.database", MONGO_DATABASE)
    .config("spark.mongodb.write.collection", MONGO_COLLECTION)
    .getOrCreate()
)

# ---------------------------------------------------------------------------
# Kafka source — consume from cpg.metadata only
# ---------------------------------------------------------------------------
raw = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
    .option("subscribe", KAFKA_TOPIC)
    .option("startingOffsets", "earliest")
    .load()
)

metadata_df = raw.select(from_json(col("value").cast("string"), schema).alias("data")).select(
    "data.*"
)


# ---------------------------------------------------------------------------
# MongoDB sink — replace/upsert by file_id for idempotent replay
# ---------------------------------------------------------------------------
def write_batch(batch_df, batch_id):
    """Write each micro-batch with replace/upsert semantics by file_id."""

    batch_df = batch_df.persist(StorageLevel.MEMORY_AND_DISK)
    try:
        row_count = batch_df.count()
        if row_count == 0:
            return

        print(f"[Batch {batch_id}] Writing {row_count} metadata document(s) to MongoDB")

        (
            batch_df.write.format("mongodb")
            .mode("append")
            .option("spark.mongodb.write.database", MONGO_DATABASE)
            .option("spark.mongodb.write.collection", MONGO_COLLECTION)
            .option("spark.mongodb.write.operationType", "replace")
            .option("spark.mongodb.write.idFieldList", "file_id")
            .option("spark.mongodb.write.upsertDocument", "true")
            .save()
        )
    finally:
        batch_df.unpersist()


# ---------------------------------------------------------------------------
# Start streaming query with processing time trigger
# ---------------------------------------------------------------------------
query = (
    metadata_df.writeStream.foreachBatch(write_batch)
    .option("checkpointLocation", CHECKPOINT_PATH)
    .trigger(processingTime=TRIGGER_INTERVAL)
    .start()
)

print("Streaming query started. Waiting for termination...")


# Graceful shutdown on SIGTERM (docker stop)
def handle_sigterm(signum, frame):
    print("Received SIGTERM — stopping streaming query...")
    query.stop()
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)

try:
    query.awaitTermination()
except KeyboardInterrupt:
    print("KeyboardInterrupt — stopping streaming query...")
    query.stop()
