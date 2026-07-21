# Architecture

![Stage 2 CPG streaming architecture](_static/stage2_pipeline.png)

The editable source is [`stage2_pipeline.excalidraw`](_static/stage2_pipeline.excalidraw). It records the same dataset and pipeline route as `screenshots/stage2_manifest.json`; the exact capture time and artifact hashes remain in that validated manifest.

## Why the routes are separate

`cpg.nodes` and `cpg.edges` go directly from Kafka Connect to Neo4j. Spark is not between Kafka and Neo4j because the Neo4j sink already provides the required direct, idempotent graph upserts. Adding Spark there would create an unnecessary transformation and checkpoint layer.

Only `cpg.metadata` goes through Spark Structured Streaming. Spark validates and reshapes file summaries, commits Kafka offset 5, and upserts five documents into MongoDB by `file_id`. `cpg.errors` is retained as an observable failure/evidence stream.

## Services and local ports

| Service | Compose role | Local port |
|---|---|---:|
| Kafka broker | Four CPG topics | `9092` |
| Kafka Connect | Neo4j sink REST API | `8083` |
| Neo4j | Browser / Bolt | `7474` / `7687` |
| MongoDB | Metadata store | `27017` |
| Mongo Express | Read-only evidence profile | `127.0.0.1:8081` |
| Spark | Structured Streaming worker | internal only |

The Mongo Express service is excluded from the default stack, read-only, and bound to localhost. The clean run is accepted from direct queries and the hash-validated manifest; no synthetic UI screenshot is used.

## Reproduce

```bash
NEO4J_PASSWORD=<local-lab-password> \
RESET_DOCKER_STATE=1 \
CONNECT_WAIT_SECONDS=180 \
SPARK_WAIT_SECONDS=90 \
SPARK_COMMIT_WAIT_SECONDS=300 \
SPARK_MONGO_WAIT_SECONDS=300 \
bash scripts/run_stage2_evidence.sh
```

Then validate the captured contract:

```bash
python3 scripts/stage2_evidence_manifest.py validate --root .
```
