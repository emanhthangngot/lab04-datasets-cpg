# Stage 1 Team Handoff Messages

Use this file to copy small messages to Truc, Thanh, and Tuan. These messages
follow the current repository layout and the lightweight OpenSpec-style SDD
workflow. The OpenSpec CLI is not required.

## Message 1 - General Announcement

````md
Team oi, bat dau Stage 1 foundation cho 3 mang con lai theo workflow
SDD/OpenSpec-style.

Luu y: minh KHONG can cai OpenSpec CLI. Chi dung folder `openspec/` trong repo
de doc spec/task truoc khi code.

Nguyen tac chung:
- Tri da khoa schema contract v1.0.
- Khong tu doi schema, field name, topic name, connector class, ID semantics,
  unresolved-call behavior.
- Truoc khi code phai doc spec, chay check, roi moi lam.
- Neu co blocker thi ghi vao tracker cua minh trong `docs/team/`.
````

## Message 2 - Baseline Commands

````md
Truoc khi bat dau, ai cung chay:

```bash
git switch dev
git pull --ff-only origin dev
git status --short
bash scripts/run_checks.sh
docker compose config
```

Neu check fail thi dung lai, copy output loi va bao vao tracker/domain cua minh
truoc khi sua tiep.
````

## Message 3 - How To Read OpenSpec

````md
Cach dung OpenSpec trong repo nay:

Khong can chay lenh `openspec`.

Doc cac file workflow chung:

```bash
cat openspec/README.md
cat openspec/changes/stage2-team-handoff/proposal.md
cat openspec/changes/stage2-team-handoff/design.md
cat openspec/changes/stage2-team-handoff/tasks.md
```

Sau do doc tiep spec theo phan minh phu trach trong `openspec/specs/`.
````

## Message 4 - Truc: Kafka/Spark

````md
@Truc phu trach Kafka/Spark Stage 1.

Doc cac file nay:

```bash
cat openspec/specs/kafka-spark/spec.md
cat docs/team/kafka-spark.md
cat schemas/cpg-events.schema.json
```

Branch:

```bash
git switch -c feature/truc/kafka-spark-stage1
```

Muc tieu:
- Verify 4 Kafka topics: `cpg.nodes`, `cpg.edges`, `cpg.metadata`, `cpg.errors`
- Verify Kafka Connect plugin dung class:
  `org.neo4j.connectors.kafka.sink.Neo4jConnector`
- Verify Spark chi consume `cpg.metadata`
- Verify Spark submit command chay trong Docker Compose
- Neu co blocker thi ghi vao `docs/team/kafka-spark.md`

Lenh rieng can chay:

```bash
docker compose up -d
bash scripts/init_kafka_topics.sh
bash scripts/check_connect_plugins.sh
```

`bash scripts/check_connect_plugins.sh` chi pass khi Kafka Connect dang reachable
o `http://localhost:8083`. Output can cho evidence la class:
`org.neo4j.connectors.kafka.sink.Neo4jConnector`.

Spark command dung la:

```bash
docker compose exec spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /app/spark_jobs/metadata_stream_to_mongo.py
```

Khong dung path noi bo cua Bitnami image. Repo duoc mount vao `/app`.
````

## Message 5 - Thanh: Neo4j/MongoDB

````md
@Thanh phu trach Neo4j/MongoDB Stage 1.

Doc cac file nay:

```bash
cat openspec/specs/graph-stores/spec.md
cat docs/team/graph-stores.md
cat schemas/cpg-events.schema.json
cat neo4j/sink_connector.json
cat spark_jobs/metadata_stream_to_mongo.py
```

Branch:

```bash
git switch -c feature/thanh/graph-stores-stage1
```

Muc tieu:
- Verify Neo4j nhan graph topology truc tiep tu Kafka Connect
- Verify Cypher chi dung field co trong JSON Schema
- Verify edge MERGE tao duoc placeholder endpoint node
- Verify node upsert that set `placeholder = false`
- Verify Cypher dung `coalesce(event.properties,{})`
- Verify MongoDB metadata replace/upsert theo `file_id`
- Chuan bi duplicate-check queries cho replay

Lenh rieng can chay:

```bash
docker compose up -d
bash scripts/check_connect_plugins.sh
docker compose exec -T neo4j cypher-shell -u neo4j -p password < neo4j/constraints.cypher
```

Neu co blocker thi ghi vao `docs/team/graph-stores.md`.
````

## Message 6 - Thanh: Duplicate-Check Queries

````md
@Thanh chuan bi them cac duplicate-check query nay cho replay evidence.

Neo4j node duplicate:

```cypher
MATCH (n:CPGNode)
WITH n.id AS id, count(*) AS c
WHERE c > 1
RETURN id, c;
```

Neo4j edge duplicate:

```cypher
MATCH ()-[r:CPG_EDGE]->()
WITH r.id AS id, count(*) AS c
WHERE c > 1
RETURN id, c;
```

Mongo metadata count:

```javascript
db.file_metadata.countDocuments()
```

Mongo metadata duplicate by `file_id`:

```javascript
db.file_metadata.aggregate([
  { $group: { _id: "$file_id", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])
```

Luu y: MongoDB collection dung la `file_metadata`. `/mnt/checkpoints/cpg_metadata`
la Spark checkpoint path, khong phai collection.
````

## Message 7 - Tuan: Evidence Book

````md
@Tuan phu trach Evidence Book Stage 1.

Doc cac file nay:

```bash
cat openspec/specs/evidence-book/spec.md
cat docs/team/evidence-book.md
cat book/_toc.yml
cat book/index.md
```

Branch:

```bash
git switch -c feature/tuan/evidence-book-stage1
```

Muc tieu:
- Verify notebook skeleton du cho cac task
- Verify screenshot folders du cho evidence Kafka, Neo4j, MongoDB, Spark, replay
- Verify Jupyter Book structure build duoc khi dependency co san
- Khong commit secret/token/private key/local credential
- Chuan hoa evidence rule: screenshot/log phai co task, command, ngay chay, ket qua

Lenh rieng neu may co Jupyter Book:

```bash
jupyter-book build book/
```

Luu y: repo hien dung `book/index.md` lam root page theo `book/_toc.yml`.
Neu thieu `jupyter-book`, ghi blocker vao `docs/team/evidence-book.md`, khong tu
y bo qua.
````

## Message 8 - PR Rules

````md
Quy dinh PR:

- PR vao branch `dev`
- Khong merge thang vao `dev`
- PR phai ghi ro:
  - Da doc spec nao
  - Da chay command nao
  - Command nao pass/fail
  - Evidence attach o dau
  - Blocker con lai neu co

Reviewer/approval schema contract van la Tri.
Neu can doi schema/field/topic/connector behavior thi phai bao truoc, khong tu sua.
````

## Message 9 - If Using AI/Codex

````md
Neu dung AI/Codex, prompt dau tien nen la:

"Ban dang lam trong repo Lab04 CPG Streaming. Truoc khi sua file, hay doc
`.codex/constitution.md`, `.codex/context/lab04-cpg.md`, `README.md` muc
SDD Task Intake, `openspec/README.md`, spec mang cua toi trong
`openspec/specs/.../spec.md`, task checklist trong
`openspec/changes/stage2-team-handoff/tasks.md`, va tracker cua toi trong
`docs/team/...`.

Sau do kiem tra `git status --short`, chay baseline checks, roi moi implement
thay doi nho nhat. Khong doi schema contract neu chua co Tri approve."

Sau khi AI lam xong, bat AI bao lai:
- File da sua
- Command da chay
- Pass/fail
- Evidence da co
- Blocker con lai
````

## Message 10 - Done Criteria

````md
Mot task chi duoc tick done khi co du:

1. Da doc dung OpenSpec/spec/task file.
2. Da chay baseline checks.
3. Da attach evidence hoac ghi blocker ro rang.
4. PR vao `dev` khong doi schema contract ngoai pham vi duoc giao.

Neu thieu evidence thi chua tick done.
````
