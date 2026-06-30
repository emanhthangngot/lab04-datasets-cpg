"""Spark Structured Streaming job for Lab04 metadata ingestion.

TODO: Run inside the Spark container with both packages:
org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0
org.mongodb.spark:mongo-spark-connector_2.12:10.3.0
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import LongType, StringType, StructType


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


spark = (
    SparkSession.builder.appName("CPGMetadataIngestion")
    .config("spark.mongodb.write.connection.uri", "mongodb://mongo:27017/")
    .config("spark.mongodb.write.database", "cpg")
    .config("spark.mongodb.write.collection", "file_metadata")
    .getOrCreate()
)

raw = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "cpg.metadata")
    .option("startingOffsets", "earliest")
    .load()
)

metadata_df = raw.select(from_json(col("value").cast("string"), schema).alias("data")).select(
    "data.*"
)


def write_batch(batch_df, batch_id):
    """Write each micro-batch with replace/upsert semantics by file_id."""

    # TODO: Verify connector option names against the installed MongoDB Spark
    # Connector version in the lab container.
    (
        batch_df.write.format("mongodb")
        .mode("append")
        .option("database", "cpg")
        .option("collection", "file_metadata")
        .option("operationType", "replace")
        .option("idFieldList", "file_id")
        .option("upsertDocument", "true")
        .save()
    )


query = (
    metadata_df.writeStream.foreachBatch(write_batch)
    .option("checkpointLocation", "/mnt/checkpoints/cpg_metadata")
    .start()
)

query.awaitTermination()
