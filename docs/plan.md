# Lab04 Hugging Face Datasets CPG Streaming Plan — FULL FINAL v2

## Final repository

Nhóm chọn repository:

```bash
https://github.com/huggingface/datasets
```

Phạm vi parse chính:

```text
src/datasets/**/*.py
```

Loại trừ:

```text
tests/**         # không phải core library
docs/**          # documentation
notebooks/**     # demo notebooks
benchmarks/**    # benchmark scripts
templates/**     # dataset templates
__pycache__/**   # compiled cache
setup.py         # package setup
```

Lưu ý: không loại `src/datasets/utils/` vì đây là core library code. Top-level `utils` nếu có sẽ không được chọn vì filter chỉ lấy `src/datasets/**/*.py`.

---

## Runtime-blocking fixes đã incorporate

1. Tất cả CLI tools chạy qua Docker Compose service context:
   - `kafka-topics.sh` chạy trong Kafka container.
   - `kafka-consumer-groups.sh` chạy trong Kafka container.
   - `cypher-shell` chạy trong Neo4j container.
   - `spark-submit` chạy trong Spark container.

2. Spark job có đủ cả 2 packages:
   - Kafka source package: `org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0`
   - MongoDB connector package: `org.mongodb.spark:mongo-spark-connector_2.12:10.3.0`

3. `producer.flush()` sau mỗi file.

4. Kafka topics được tạo explicit, không rely vào auto-create.

5. Neo4j chỉ tạo node uniqueness constraint mặc định, không tạo relationship uniqueness constraint mặc định.

6. Node `properties` luôn là `{}`, không bao giờ là `null`; Cypher có thêm `coalesce(event.properties, {})`.

7. Metadata tính `num_total_edges` explicit bằng `cfg_count + dfg_count + call_count`.

8. Replay dùng `file_id + run_id` để cleanup stale nodes/edges.

---

# 1. Architecture

```text
GitHub repository: huggingface/datasets
        |
        v
Repository Cloner + File Discovery
        |
        v
Parser Service
Python ast-based incremental parser
AST / CFG / DFG / Call extraction
        |
        v
Apache Kafka
+----------------+----------------+----------------+----------------+
| cpg.nodes      | cpg.edges      | cpg.metadata   | cpg.errors     |
+----------------+----------------+----------------+----------------+
        |                |                |                |
        |                |                |                |
        +--------+-------+                |                |
                 |                        |                |
                 v                        v                v
        Neo4j Kafka Connector       Spark Structured       Logs / Monitoring
        Sink                        Streaming
                 |                        |
                 v                        v
              Neo4j                    MongoDB
        CPG graph topology       Source code metadata
```

Graph topology:

```text
Parser Service -> Kafka -> Neo4j Kafka Connector -> Neo4j
```

Metadata:

```text
Parser Service -> Kafka -> Spark Structured Streaming -> MongoDB
```

Spark không được nằm giữa Kafka và Neo4j.

---

# 2. Why `huggingface/datasets`

`huggingface/datasets` phù hợp vì:

- Repo chính thức của Hugging Face.
- Chủ yếu là Python.
- Có source chính rõ ở `src/datasets`.
- Có nhiều class, function, call, assignment và data-processing logic để demo AST/CFG/DFG/CALL.
- Domain dễ giải thích: thư viện dùng để load và xử lý datasets cho AI/ML.
- Quy mô lớn hơn `peft`, nên cần filter source scope kỹ.

---

# 3. Folder structure

```text
lab04-datasets-cpg/
├── README.md
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── scripts/
│   ├── clone_repo.sh
│   ├── init_kafka_topics.sh
│   ├── check_connect_plugins.sh
│   ├── register_neo4j_sink.sh
│   ├── wait_neo4j_connector_idle.sh
│   ├── run_replay_demo.sh
│   └── publish_book.sh
├── parser_service/
│   ├── __init__.py
│   ├── config.py
│   ├── discover.py
│   ├── ids.py
│   ├── schemas.py
│   ├── ast_extractor.py
│   ├── cfg_extractor.py
│   ├── dfg_extractor.py
│   ├── call_extractor.py
│   ├── producer.py
│   ├── parser.py
│   └── main.py
├── spark_jobs/
│   └── metadata_stream_to_mongo.py
├── neo4j/
│   ├── constraints.cypher
│   ├── cleanup_stale.cypher
│   └── sink_connector.json
├── notebooks/
│   ├── 01_repository_discovery.ipynb
│   ├── 02_parser_service.ipynb
│   ├── 03_kafka_topics.ipynb
│   ├── 04_neo4j_ingestion.ipynb
│   ├── 05_mongodb_metadata.ipynb
│   └── 06_idempotent_replay.ipynb
├── book/
│   ├── _config.yml
│   ├── _toc.yml
│   ├── index.md
│   ├── task1_repository.md
│   ├── task2_parser.md
│   ├── task3_kafka.md
│   ├── task4_neo4j.md
│   ├── task5_mongodb.md
│   ├── task6_replay.md
│   ├── architecture.md
│   └── reflection.md
└── screenshots/
    ├── kafka/
    ├── neo4j/
    ├── mongodb/
    ├── spark/
    └── replay/
```

---

# 4. Task 1 — Repository Cloning and File Discovery

## 4.1 Clone repository

File: `scripts/clone_repo.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

mkdir -p data

if [ ! -d "data/datasets/.git" ]; then
  git clone --depth 1 https://github.com/huggingface/datasets.git data/datasets
else
  echo "Repository already cloned."
fi

cd data/datasets
echo "Commit SHA:"
git rev-parse HEAD
```

Run:

```bash
chmod +x scripts/clone_repo.sh
bash scripts/clone_repo.sh
```

## 4.2 File discovery

File: `parser_service/discover.py`

```python
from pathlib import Path

EXCLUDED_PARTS = {
    "tests",
    "docs",
    "notebooks",
    "benchmarks",
    "templates",
    "__pycache__",
}

def discover_python_files(repo_root: Path) -> list[Path]:
    source_root = repo_root / "src" / "datasets"
    all_py_files = sorted(repo_root.rglob("*.py"))
    selected_files = []

    for path in all_py_files:
        if path.name == "setup.py":
            continue

        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue

        if source_root in path.parents or path == source_root:
            selected_files.append(path)

    return selected_files
```

Notebook evidence:

```python
from pathlib import Path
from parser_service.discover import discover_python_files

repo_root = Path("data/datasets")
all_py = sorted(repo_root.rglob("*.py"))
selected = discover_python_files(repo_root)

print("Total .py files discovered:", len(all_py))
print("Selected .py files:", len(selected))

for p in selected[:20]:
    print(p.relative_to(repo_root).as_posix())
```

Report text:

```text
The repository contains many Python files across source, tests, documentation and utility folders.
We focus on src/datasets/**/*.py because it represents the core library source code.
Tests, docs, templates and benchmark files are excluded to keep the CPG focused and the pipeline manageable.
We do not exclude src/datasets/utils because it contains core library code.
```

---

# 5. Task 2 — Incremental CPG Parser Service

## 5.1 Parser choice

Use Python standard library:

```python
import ast
```

Reason:

- Native Python.
- No JVM dependency.
- No grammar build.
- Good enough for lab-level AST/CFG/DFG/CALL extraction.
- Easy to process one file at a time with bounded memory.

Limit:

```text
This is a lab-level CPG, not a full Joern-equivalent CPG.
```

## 5.2 Event schema overview

Topics:

```text
node event      -> cpg.nodes
edge event      -> cpg.edges
metadata event  -> cpg.metadata
error event     -> cpg.errors
```

Common fields:

```text
schema_version
event_time
repo
commit_sha
run_id
file_id
file_path
```

## 5.3 Node event schema

```json
{
  "schema_version": "1.0",
  "event_time": "2026-06-24T10:00:00.000Z",
  "op": "upsert",
  "repo": "huggingface/datasets",
  "commit_sha": "...",
  "run_id": "...",
  "file_id": "...",
  "file_path": "src/datasets/arrow_dataset.py",
  "id": "...",
  "node_type": "FunctionDef",
  "scope_path": "Dataset.map",
  "lineno": 42,
  "col_offset": 4,
  "end_lineno": 80,
  "end_col_offset": 20,
  "properties": {
    "name": "map"
  }
}
```

Important:

```text
properties must always be a map.
Use {} when no extra properties exist.
Never emit properties: null.
```

## 5.4 Edge event schema

```json
{
  "schema_version": "1.0",
  "event_time": "2026-06-24T10:00:00.000Z",
  "op": "upsert",
  "repo": "huggingface/datasets",
  "commit_sha": "...",
  "run_id": "...",
  "file_id": "...",
  "file_path": "src/datasets/arrow_dataset.py",
  "id": "...",
  "source_id": "...",
  "target_id": "...",
  "edge_type": "CFG_NEXT",
  "properties": {
    "scope_path": "Dataset.map"
  }
}
```

## 5.5 Metadata event schema

```json
{
  "schema_version": "1.0",
  "event_time": "2026-06-24T10:00:00.000Z",
  "repo": "huggingface/datasets",
  "commit_sha": "...",
  "run_id": "...",
  "file_id": "...",
  "file_path": "src/datasets/arrow_dataset.py",
  "file_size": 12345,
  "content_hash": "...",
  "num_ast_nodes": 120,
  "num_cfg_edges": 40,
  "num_dfg_edges": 25,
  "num_call_edges": 18,
  "num_total_edges": 83,
  "parse_duration_ms": 73,
  "status": "success"
}
```

## 5.6 Error event schema

```json
{
  "schema_version": "1.0",
  "event_time": "2026-06-24T10:00:00.000Z",
  "repo": "huggingface/datasets",
  "commit_sha": "...",
  "run_id": "...",
  "file_id": "...",
  "file_path": "src/datasets/broken.py",
  "status": "failed",
  "error_type": "SyntaxError",
  "message": "invalid syntax",
  "lineno": 42,
  "col_offset": 7
}
```

`col_offset` is zero-based. If Python does not expose parser location data,
emit `null` for `lineno` and `col_offset`.

---

# 6. Event builders and schema guards

File: `parser_service/schemas.py`

```python
def build_node_event(
    *,
    schema_version: str,
    event_time: str,
    repo: str,
    commit_sha: str,
    run_id: str,
    file_id: str,
    file_path: str,
    node_id: str,
    node_type: str,
    scope_path: str,
    lineno: int | None,
    col_offset: int | None,
    end_lineno: int | None,
    end_col_offset: int | None,
    properties: dict | None = None,
) -> dict:
    return {
        "schema_version": schema_version,
        "event_time": event_time,
        "op": "upsert",
        "repo": repo,
        "commit_sha": commit_sha,
        "run_id": run_id,
        "file_id": file_id,
        "file_path": file_path,
        "id": node_id,
        "node_type": node_type,
        "scope_path": scope_path,
        "lineno": lineno,
        "col_offset": col_offset,
        "end_lineno": end_lineno,
        "end_col_offset": end_col_offset,
        "properties": properties or {},
    }
```

Reason:

```text
Neo4j Cypher uses SET n += event.properties.
Therefore event.properties must always be a map.
```

---

# 7. ID generation

File: `parser_service/ids.py`

```python
import ast
import hashlib
from pathlib import Path

def short_hash(raw: str, n: int = 16) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:n]

def normalize_relative_path(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()

def make_file_id(repo_name: str, relative_path: str) -> str:
    return short_hash(f"{repo_name}:{relative_path}")

def make_content_hash(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()

def extract_assignment_target(node: ast.AST) -> str:
    try:
        if isinstance(node, ast.Assign) and node.targets:
            return ast.unparse(node.targets[0])
        if isinstance(node, ast.AnnAssign):
            return ast.unparse(node.target)
        if isinstance(node, ast.AugAssign):
            return ast.unparse(node.target)
    except Exception:
        return "unknown"
    return "unknown"

def make_node_id(file_id: str, node: ast.AST, scope_path: str) -> str:
    node_type = type(node).__name__

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        raw = f"{file_id}:{scope_path}:{node_type}:{node.name}"

    elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        target = extract_assignment_target(node)
        lineno = getattr(node, "lineno", -1)
        raw = f"{file_id}:{scope_path}:{node_type}:{target}:{lineno}"

    else:
        lineno = getattr(node, "lineno", -1)
        col_offset = getattr(node, "col_offset", -1)
        raw = f"{file_id}:{scope_path}:{node_type}:{lineno}:{col_offset}"

    return short_hash(raw)

def make_edge_id(source_id: str, target_id: str, edge_type: str) -> str:
    return short_hash(f"{source_id}:{target_id}:{edge_type}")
```

Report limitation:

```text
Named nodes use name-based stable IDs.
Anonymous nodes use line/column-based IDs and may change after large edits.
Stale entities are handled by file_id + run_id cleanup during replay.
```

---

# 8. Extraction scope

AST nodes:

```text
Module
Import
ImportFrom
ClassDef
FunctionDef
AsyncFunctionDef
Assign
AnnAssign
AugAssign
Return
If
For
While
Try
With
Call
Name
Attribute
Constant
BinOp
Compare
```

CFG edges:

```text
CFG_NEXT
CFG_TRUE
CFG_FALSE
CFG_LOOP_BODY
CFG_LOOP_BACK
CFG_RETURN
```

DFG edges:

```text
DFG_DEF_USE
```

Call edges:

```text
CALL_RESOLVED
CALL_UNRESOLVED
```

Two-pass call extraction:

```python
def collect_local_defs(tree):
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }

def get_callee_name(func):
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None
```

---

# 9. Kafka topic creation — Docker-safe

File: `scripts/init_kafka_topics.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

KAFKA_SERVICE=${KAFKA_SERVICE:-broker}
BOOTSTRAP=${BOOTSTRAP_SERVERS_IN_CONTAINER:-localhost:9092}

echo "Creating Kafka topics inside service: $KAFKA_SERVICE"

docker compose exec "$KAFKA_SERVICE" kafka-topics.sh   --bootstrap-server "$BOOTSTRAP"   --create --if-not-exists   --topic cpg.nodes   --partitions 4   --replication-factor 1   --config retention.ms=86400000

docker compose exec "$KAFKA_SERVICE" kafka-topics.sh   --bootstrap-server "$BOOTSTRAP"   --create --if-not-exists   --topic cpg.edges   --partitions 4   --replication-factor 1   --config retention.ms=86400000

docker compose exec "$KAFKA_SERVICE" kafka-topics.sh   --bootstrap-server "$BOOTSTRAP"   --create --if-not-exists   --topic cpg.metadata   --partitions 1   --replication-factor 1   --config retention.ms=86400000

docker compose exec "$KAFKA_SERVICE" kafka-topics.sh   --bootstrap-server "$BOOTSTRAP"   --create --if-not-exists   --topic cpg.errors   --partitions 1   --replication-factor 1   --config retention.ms=86400000

echo "Kafka topics created."
docker compose exec "$KAFKA_SERVICE" kafka-topics.sh   --bootstrap-server "$BOOTSTRAP"   --list
```

Kafka CLI binary path note:

```text
This plan assumes the Kafka image exposes kafka-topics.sh and kafka-consumer-groups.sh on PATH inside the Kafka service container.
If the selected image does not expose them on PATH, use full paths such as:
/opt/kafka/bin/kafka-topics.sh
/opt/kafka/bin/kafka-consumer-groups.sh
```

---

# 10. Kafka producer

File: `parser_service/producer.py`

```python
import json
from kafka import KafkaProducer

def build_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
        retries=3,
        linger_ms=10,
    )
```

---

# 11. Parser process_file pattern — explicit total_edges and flush

File: `parser_service/parser.py`

```python
import ast
import gc
import time
from pathlib import Path

def process_file(file_path: Path, producer, context) -> dict:
    start_time = time.time()
    source = None
    tree = None

    try:
        relative_path = file_path.relative_to(context.repo_root).as_posix()
        file_id = make_file_id(context.repo_name, relative_path)

        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=relative_path)

        node_count = 0
        cfg_count = 0
        dfg_count = 0
        call_count = 0

        for node_event in extract_ast_nodes_gen(
            tree=tree,
            file_id=file_id,
            file_path=relative_path,
            context=context,
        ):
            producer.send("cpg.nodes", key=file_id, value=node_event)
            node_count += 1

        for edge_event in extract_edges_gen(
            tree=tree,
            file_id=file_id,
            file_path=relative_path,
            context=context,
        ):
            producer.send("cpg.edges", key=file_id, value=edge_event)

            edge_type = edge_event["edge_type"]
            if edge_type.startswith("CFG"):
                cfg_count += 1
            elif edge_type.startswith("DFG"):
                dfg_count += 1
            elif edge_type.startswith("CALL"):
                call_count += 1

        total_edges = cfg_count + dfg_count + call_count

        metadata = build_metadata_event(
            file_id=file_id,
            file_path=relative_path,
            source=source,
            context=context,
            num_ast_nodes=node_count,
            num_cfg_edges=cfg_count,
            num_dfg_edges=dfg_count,
            num_call_edges=call_count,
            num_total_edges=total_edges,
            parse_duration_ms=int((time.time() - start_time) * 1000),
            status="success",
        )

        producer.send("cpg.metadata", key=file_id, value=metadata)
        producer.flush(timeout=30)

        return metadata

    except SyntaxError as e:
        error_event = build_error_event(
            file_path=str(file_path),
            error=e,
            context=context,
        )

        producer.send(
            "cpg.errors",
            key=error_event["file_id"],
            value=error_event,
        )

        producer.flush(timeout=30)
        return error_event

    finally:
        try:
            del source
            del tree
        except Exception:
            pass
        gc.collect()
```

Main loop:

```python
def main():
    context = build_context()
    producer = build_producer(context.bootstrap_servers)

    try:
        selected_files = discover_python_files(context.repo_root)

        for file_path in selected_files:
            process_file(file_path, producer, context)

        producer.flush(timeout=60)

    finally:
        producer.close(timeout=30)
```

---

# 12. Neo4j constraints — Docker-safe

File: `neo4j/constraints.cypher`

```cypher
CREATE CONSTRAINT cpg_node_id IF NOT EXISTS
FOR (n:CPGNode) REQUIRE n.id IS UNIQUE;
```

Do not create by default:

The example below is intentionally not included in `neo4j/constraints.cypher`
because relationship uniqueness may not be supported in the lab setup.

```cypher
CREATE CONSTRAINT cpg_edge_id IF NOT EXISTS
FOR ()-[r:CPG_EDGE]-() REQUIRE r.id IS UNIQUE;
```

Apply:

```bash
docker compose exec -T neo4j cypher-shell -u neo4j -p password   < neo4j/constraints.cypher
```

---

# 13. Neo4j Kafka Connector

## 13.1 Check connector plugin

File: `scripts/check_connect_plugins.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

CONNECT_URL=${CONNECT_URL:-http://localhost:8083}

echo "Available Kafka Connect plugins:"
curl -s "$CONNECT_URL/connector-plugins" | python3 -m json.tool

echo "Filtering Neo4j plugin:"
curl -s "$CONNECT_URL/connector-plugins" | python3 -m json.tool | grep -i neo4j || true
```

Official class:

```text
org.neo4j.connectors.kafka.sink.Neo4jConnector
```

If lab plugin prints:

```text
org.neo4j.connectors.kafka.sink.Neo4jSinkConnector
```

then use that exact class.

## 13.2 Sink connector config

File: `neo4j/sink_connector.json`

```json
{
  "name": "cpg-neo4j-sink",
  "config": {
    "connector.class": "org.neo4j.connectors.kafka.sink.Neo4jConnector",
    "tasks.max": "1",
    "topics": "cpg.nodes,cpg.edges",

    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",

    "neo4j.uri": "neo4j://neo4j:7687",
    "neo4j.authentication.type": "BASIC",
    "neo4j.authentication.basic.username": "neo4j",
    "neo4j.authentication.basic.password": "password",

    "neo4j.cypher.topic.cpg.nodes": "WITH __value AS event MERGE (n:CPGNode {id: event.id}) ON CREATE SET n.created_at = event.event_time SET n += coalesce(event.properties, {}), n.file_id = event.file_id, n.file_path = event.file_path, n.repo = event.repo, n.commit_sha = event.commit_sha, n.run_id = event.run_id, n.node_type = event.node_type, n.scope_path = event.scope_path, n.lineno = event.lineno, n.col_offset = event.col_offset, n.end_lineno = event.end_lineno, n.end_col_offset = event.end_col_offset, n.placeholder = false, n.updated_at = event.event_time",

    "neo4j.cypher.topic.cpg.edges": "WITH __value AS event MERGE (a:CPGNode {id: event.source_id}) ON CREATE SET a.placeholder = true, a.created_at = event.event_time MERGE (b:CPGNode {id: event.target_id}) ON CREATE SET b.placeholder = true, b.created_at = event.event_time MERGE (a)-[r:CPG_EDGE {id: event.id}]->(b) ON CREATE SET r.created_at = event.event_time SET r.edge_type = event.edge_type, r.file_id = event.file_id, r.file_path = event.file_path, r.repo = event.repo, r.commit_sha = event.commit_sha, r.run_id = event.run_id, r.updated_at = event.event_time"
  }
}
```

Register:

```bash
curl -X POST http://localhost:8083/connectors   -H "Content-Type: application/json"   --data @neo4j/sink_connector.json
```

---

# 14. Spark Structured Streaming to MongoDB — Docker-safe

Spark consumes:

```text
cpg.metadata
```

Spark writes:

```text
MongoDB database: cpg
MongoDB collection: file_metadata
```

Checkpoint:

```text
/mnt/checkpoints/cpg_metadata
```

## 14.1 Spark job

File: `spark_jobs/metadata_stream_to_mongo.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, LongType

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
    SparkSession.builder
    .appName("CPGMetadataIngestion")
    .config("spark.mongodb.write.connection.uri", "mongodb://mongo:27017/")
    .config("spark.mongodb.write.database", "cpg")
    .config("spark.mongodb.write.collection", "file_metadata")
    .getOrCreate()
)

raw = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "cpg.metadata")
    .option("startingOffsets", "earliest")
    .load()
)

metadata_df = (
    raw.select(from_json(col("value").cast("string"), schema).alias("data"))
    .select("data.*")
)

def write_batch(batch_df, batch_id):
    (
        batch_df.write
        .format("mongodb")
        .mode("append")
        .option("spark.mongodb.write.database", "cpg")
        .option("spark.mongodb.write.collection", "file_metadata")
        .option("spark.mongodb.write.operationType", "replace")
        .option("spark.mongodb.write.idFieldList", "file_id")
        .option("spark.mongodb.write.upsertDocument", "true")
        .save()
    )

query = (
    metadata_df.writeStream
    .foreachBatch(write_batch)
    .option("checkpointLocation", "/mnt/checkpoints/cpg_metadata")
    .start()
)

query.awaitTermination()
```

## 14.2 Run Spark job with both required packages

Do not run:

```bash
spark-submit spark_jobs/metadata_stream_to_mongo.py
```

Do run:

```bash
docker compose exec spark spark-submit   --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0   /app/spark_jobs/metadata_stream_to_mongo.py
```

Fallback if service name is `spark-master`:

```bash
docker compose exec spark-master spark-submit   --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0   /app/spark_jobs/metadata_stream_to_mongo.py
```

Important:

```text
The Kafka package version must match the Spark version.
For Spark 3.5.x, use spark-sql-kafka-0-10_2.12:3.5.0 or the exact 3.5.x version used by the container.
```

---

# 15. Replay and stale cleanup

Replay process:

```text
1. Parse all selected datasets files.
2. Record Neo4j node/edge counts.
3. Record MongoDB metadata.
4. Modify one Python file.
5. Reprocess only that file.
6. Wait for Neo4j connector to consume all messages.
7. Cleanup stale nodes/edges using file_id + run_id.
8. Verify no duplicates.
```

Target file examples:

```text
src/datasets/config.py
src/datasets/info.py
src/datasets/features/features.py
```

Modification:

```python
LAB04_REPLAY_MARKER = "replay_v2"
```

## 15.1 Wait connector before cleanup

File: `scripts/wait_neo4j_connector_idle.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

KAFKA_SERVICE=${KAFKA_SERVICE:-broker}
BOOTSTRAP=${BOOTSTRAP_SERVERS_IN_CONTAINER:-localhost:9092}
CONNECTOR_NAME=${CONNECTOR_NAME:-cpg-neo4j-sink}
GROUP="connect-${CONNECTOR_NAME}"

echo "Waiting for Neo4j connector consumer group lag to become zero..."

while true; do
  LAG=$(docker compose exec "$KAFKA_SERVICE" kafka-consumer-groups.sh     --bootstrap-server "$BOOTSTRAP"     --describe     --group "$GROUP" 2>/dev/null     | awk 'NR>1 && $6 ~ /^[0-9]+$/ {sum += $6} END {print sum+0}')

  echo "Current lag: $LAG"

  if [ "$LAG" -eq 0 ]; then
    break
  fi

  sleep 2
done

echo "Neo4j connector appears caught up."
```

## 15.2 Cleanup stale entities

File: `neo4j/cleanup_stale.cypher`

```cypher
MATCH ()-[r:CPG_EDGE {file_id: $file_id}]->()
WHERE r.run_id <> $run_id
DELETE r;

MATCH (n:CPGNode {file_id: $file_id})
WHERE n.run_id <> $run_id
DETACH DELETE n;
```

Run:

```bash
docker compose exec neo4j cypher-shell -u neo4j -p password   -P file_id="$FILE_ID"   -P run_id="$RUN_ID"   "$(cat neo4j/cleanup_stale.cypher)"
```

---

# 16. Final run order — Docker-safe

```bash
# 1. Start infra
docker compose up -d

# 2. Clone datasets
bash scripts/clone_repo.sh

# 3. Create Kafka topics explicitly inside Kafka container
bash scripts/init_kafka_topics.sh

# 4. Check connector plugin class
bash scripts/check_connect_plugins.sh

# 5. Create Neo4j node constraint only inside Neo4j container
docker compose exec -T neo4j cypher-shell -u neo4j -p password   < neo4j/constraints.cypher

# 6. Register Neo4j sink connector
bash scripts/register_neo4j_sink.sh

# 7. Start Spark metadata streaming job inside Spark container
docker compose exec spark spark-submit   --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0   /app/spark_jobs/metadata_stream_to_mongo.py

# 8. Parse selected datasets files
python -m parser_service.main --repo data/datasets --mode full

# 9. Verify Kafka, Neo4j, MongoDB in notebooks
jupyter notebook notebooks/

# 10. Run replay demo
bash scripts/run_replay_demo.sh

# 11. Build Jupyter Book
jupyter-book build book/

# 12. Publish GitHub Pages
bash scripts/publish_book.sh
```

---

# 17. Evidence checklist

Kafka evidence:

```text
cpg.nodes
cpg.edges
cpg.metadata
cpg.errors
```

Producer evidence:

```text
producer.send() is asynchronous, so parser calls producer.flush() after each processed file and closes the producer at the end.
```

Metadata evidence:

```text
num_total_edges = num_cfg_edges + num_dfg_edges + num_call_edges
```

Neo4j evidence:

```cypher
MATCH (n:CPGNode) RETURN count(n);
MATCH ()-[r:CPG_EDGE]->() RETURN count(r);
MATCH (n:CPGNode) WITH n.id AS id, count(*) AS c WHERE c > 1 RETURN id, c;
MATCH ()-[r:CPG_EDGE]->() WITH r.id AS id, count(*) AS c WHERE c > 1 RETURN id, c;
MATCH (n:CPGNode {placeholder: true}) RETURN count(n);
```

MongoDB evidence:

```javascript
db.file_metadata.countDocuments()

db.file_metadata.aggregate([
  { $group: { _id: "$file_id", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])
```

Replay evidence:

```text
Before/after modified file content_hash
Before/after run_id
Before/after Neo4j file node count
Before/after Neo4j file edge count
No duplicate nodes
No duplicate edges
MongoDB document replaced, not duplicated
Spark checkpoint path exists
```

---

# 18. Team split

Member 1 — Parser Service:

```text
file discovery
stable ID
AST extraction
CFG extraction
DFG extraction
two-pass call extraction
Kafka producer integration
producer.flush()
properties never null
num_total_edges explicit
```

Member 2 — Kafka + Neo4j:

```text
Docker Compose infra
Kafka topic creation via docker compose exec
Kafka Connect plugin check
Neo4j constraints via docker compose exec -T
Neo4j sink connector config
Cypher MERGE with coalesce(event.properties, {})
Neo4j verification queries
consumer lag check via docker compose exec
```

Member 3 — Spark + MongoDB + Report:

```text
Spark Structured Streaming job
spark-submit via docker compose exec
Kafka source package + MongoDB connector package
MongoDB replace/upsert by file_id
checkpoint verification
replay demo
Jupyter Book
screenshots
final reflection
```

---

# 19. Timeline

Day 1:

```text
Clone datasets
Count .py files
Prepare docker-compose
Start Kafka, Kafka Connect, Neo4j, MongoDB, Spark
Create architecture diagram draft
```

Day 2:

```text
Implement file discovery
Implement file_id/node_id
Extract AST nodes
Ensure properties is always {}
Emit cpg.nodes and cpg.metadata
Add producer.flush()
```

Day 3:

```text
Implement basic CFG
Implement basic DFG
Implement two-pass call extraction
Emit cpg.edges and cpg.errors
Compute num_total_edges explicitly
```

Day 4:

```text
Create Kafka topics inside container
Check Neo4j connector plugin
Create Neo4j node constraint inside container
Register connector
Verify node/edge ingestion
```

Day 5:

```text
Run spark-submit inside Spark container with both Kafka and Mongo packages
Read cpg.metadata
Write MongoDB with replace/upsert by file_id
Verify checkpoint
Verify num_total_edges consistency
```

Day 6:

```text
Modify one datasets file
Reprocess only that file
Wait for connector lag to become zero
Run stale cleanup
Verify no duplicates and metadata update
```

Day 7:

```text
Write Jupyter Book
Insert notebook outputs and screenshots
Publish GitHub Pages
Submit root URL
```

---

# 20. Risk register

| Risk | Severity | Fix |
|---|---:|---|
| CLI tools not available on host | Critical | Run through `docker compose exec` |
| Spark Kafka source package missing | Critical | Add `org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0` |
| Producer messages lost | Critical | Use `producer.flush()` after each file |
| Wrong Neo4j connector class | Critical | Check `/connector-plugins` |
| Kafka KRaft broker missing cluster ID | Critical | Set `CLUSTER_ID` in Compose |
| Relationship constraint unsupported | Moderate | Only create node uniqueness constraint |
| `event.properties` is null | Moderate | Emit `{}` and use `coalesce(event.properties, {})` |
| `num_total_edges` inconsistent | Moderate | Compute explicitly in `process_file` |
| Spark checkpoint lost | Critical | Use persistent mounted volume |
| Cleanup races connector ingestion | Moderate | Wait for connector lag to become zero |
| Kafka topics auto-created with bad config | Moderate | Create topics explicitly |

---

# 21. Final limitations for report

```text
The parser implements a lab-level CPG rather than a full production-grade Joern-equivalent CPG.

CFG is limited to common Python control structures such as sequential statements, if, loop and return.

DFG is intra-procedural and focuses on local variable def-use relationships.

Call resolution is local-file based and does not fully resolve imports, aliases, inheritance or dynamic dispatch.

Anonymous AST node IDs may change after large edits. This is handled by file-level run_id cleanup during replay.

The system demonstrates incremental replay at file granularity, not function-level incremental diffing.
```

---

# 22. Final conclusion for report

```text
This implementation uses an incremental ast-based Parser Service to process Hugging Face Datasets Python source files one by one and emit CPG node, edge, metadata and error events to Kafka. The graph topology is ingested directly from Kafka into Neo4j through the Neo4j Kafka Connector Sink using Cypher MERGE operations for idempotency. Source metadata is processed by Spark Structured Streaming and written to MongoDB with checkpointing and upsert semantics. The Spark submit command includes both the Kafka source package and the MongoDB Spark Connector package.

To avoid runtime failures, the pipeline explicitly creates all Kafka topics from inside the Kafka container, flushes the Kafka producer after each file, uses only a Neo4j node uniqueness constraint that is safe for the lab environment, runs cypher-shell and spark-submit inside their containers, and avoids relying on relationship constraints. The replay demonstration modifies one Python file and reprocesses only that file. The system verifies that Neo4j and MongoDB reflect the updated state without duplicate graph elements or duplicate metadata documents.
```

---

# 23. Expected score

```text
Task 1 Repository Cloning and File Discovery: 1 / 1
Task 2 Incremental CPG Parser Service: 1.3–1.5 / 1.5
Task 3 Kafka Topic Design: 1.5 / 1.5
Task 4 Graph Topology Ingestion into Neo4j: 1.7–2 / 2
Task 5 Source Metadata Ingestion into MongoDB: 1.7–2 / 2
Task 6 Idempotent Replay Verification: 0.8–1 / 1
Architecture Diagram: 1 / 1

Expected total: 8.8–10 / 10
```
