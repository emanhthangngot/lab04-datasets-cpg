# Tin Nhắn Giao Việc Stage 1 Cho Team

File này dùng để copy từng tin nhắn nhỏ gửi cho Trực, Thành và Tuấn. Nội dung
đã được rà theo layout hiện tại của repo và workflow SDD/OpenSpec-style trong
repo. Dùng các lệnh `/sdd/specify`, `/sdd/plan`, `/sdd/tasks`; artifact đã duyệt
được lưu trong `openspec/`.

## Tin 1 - Thông Báo Chung

````md
Team ơi, bắt đầu Stage 1 foundation cho 3 mảng còn lại theo workflow
SDD/OpenSpec-style.

Lưu ý: workflow OpenSpec của repo đi qua lệnh `/sdd/*` và folder `openspec/`.
Đọc spec/task trước khi code.

Nguyên tắc chung:
- Trí đã khóa schema contract v1.0.
- Không tự đổi schema, field name, topic name, connector class, ID semantics,
  unresolved-call behavior.
- Trước khi code phải đọc spec, chạy check, rồi mới làm.
- Nếu có blocker thì ghi vào tracker của mình trong `docs/team/`.
````

## Tin 2 - Lệnh Chung Trước Khi Làm

````md
Trước khi bắt đầu, ai cũng chạy:

```bash
git switch dev
git pull --ff-only origin dev
git status --short
bash scripts/run_checks.sh
docker compose config
```

Nếu check fail thì dừng lại, copy output lỗi và báo vào tracker/domain của mình
trước khi sửa tiếp.
````

## Tin 3 - Cách Đọc OpenSpec

````md
Cách dùng OpenSpec trong repo này:

Dùng lệnh repo-local `/sdd/specify`, `/sdd/plan`, `/sdd/tasks` khi cần tạo hoặc
cập nhật spec; sau đó đọc artifact trong `openspec/`.

Đọc các file workflow chung:

```bash
cat openspec/README.md
cat openspec/changes/stage2-team-handoff/proposal.md
cat openspec/changes/stage2-team-handoff/design.md
cat openspec/changes/stage2-team-handoff/tasks.md
```

Sau đó đọc tiếp spec theo phần mình phụ trách trong `openspec/specs/`.
````

## Tin 4 - Trực: Kafka/Spark

````md
@Trực phụ trách Kafka/Spark Stage 1.

Đọc các file này:

```bash
cat openspec/specs/kafka-spark/spec.md
cat docs/team/kafka-spark.md
cat schemas/cpg-events.schema.json
```

Branch:

```bash
git switch -c feature/truc/kafka-spark-stage1
```

Mục tiêu:
- Verify 4 Kafka topics: `cpg.nodes`, `cpg.edges`, `cpg.metadata`, `cpg.errors`
- Verify Kafka Connect plugin đúng class:
  `org.neo4j.connectors.kafka.sink.Neo4jConnector`
- Verify Spark chỉ consume `cpg.metadata`
- Verify Spark submit command chạy trong Docker Compose
- Nếu có blocker thì ghi vào `docs/team/kafka-spark.md`

Lệnh riêng cần chạy:

```bash
docker compose up -d
bash scripts/init_kafka_topics.sh
bash scripts/check_connect_plugins.sh
```

`bash scripts/check_connect_plugins.sh` chỉ pass khi Kafka Connect đang reachable
ở `http://localhost:8083`. Output cần cho evidence là class:
`org.neo4j.connectors.kafka.sink.Neo4jConnector`.

Spark command đúng là:

```bash
docker compose exec spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /app/spark_jobs/metadata_stream_to_mongo.py
```

Không dùng path nội bộ của Bitnami image. Repo được mount vào `/app`.
````

## Tin 5 - Thành: Neo4j/MongoDB

````md
@Thành phụ trách Neo4j/MongoDB Stage 1.

Đọc các file này:

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

Mục tiêu:
- Verify Neo4j nhận graph topology trực tiếp từ Kafka Connect
- Verify Cypher chỉ dùng field có trong JSON Schema
- Verify edge MERGE tạo được placeholder endpoint node
- Verify node upsert thật set `placeholder = false`
- Verify Cypher dùng `coalesce(event.properties,{})`
- Verify MongoDB metadata replace/upsert theo `file_id`
- Chuẩn bị duplicate-check queries cho replay

Lệnh riêng cần chạy:

```bash
docker compose up -d
bash scripts/check_connect_plugins.sh
docker compose exec -T neo4j cypher-shell -u neo4j -p password < neo4j/constraints.cypher
```

Nếu có blocker thì ghi vào `docs/team/graph-stores.md`.
````

## Tin 6 - Thành: Duplicate-Check Queries

````md
@Thành chuẩn bị thêm các duplicate-check query này cho replay evidence.

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

Lưu ý: MongoDB collection đúng là `file_metadata`. `/mnt/checkpoints/cpg_metadata`
là Spark checkpoint path, không phải collection.
````

## Tin 7 - Tuấn: Evidence Book

````md
@Tuấn phụ trách Evidence Book Stage 1.

Đọc các file này:

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

Mục tiêu:
- Verify notebook skeleton đủ cho các task
- Verify screenshot folders đủ cho evidence Kafka, Neo4j, MongoDB, Spark, replay
- Verify Jupyter Book structure build được khi dependency có sẵn
- Không commit secret/token/private key/local credential
- Chuẩn hóa evidence rule: screenshot/log phải có task, command, ngày chạy, kết quả

Lệnh riêng nếu máy có Jupyter Book:

```bash
jupyter-book build book/
```

Lưu ý: repo hiện dùng `book/index.md` làm root page theo `book/_toc.yml`.
Nếu thiếu `jupyter-book`, ghi blocker vào `docs/team/evidence-book.md`, không tự
ý bỏ qua.
````

## Tin 8 - Quy Định PR

````md
Quy định PR:

- PR vào branch `dev`
- Không merge thẳng vào `dev`
- PR phải ghi rõ:
  - Đã đọc spec nào
  - Đã chạy command nào
  - Command nào pass/fail
  - Evidence attach ở đâu
  - Blocker còn lại nếu có

Reviewer/approval schema contract vẫn là Trí.
Nếu cần đổi schema/field/topic/connector behavior thì phải báo trước, không tự sửa.
````

## Tin 9 - Nếu Dùng AI/Codex

````md
Nếu dùng AI/Codex, prompt đầu tiên nên là:

"Bạn đang làm trong repo Lab04 CPG Streaming. Trước khi sửa file, hãy đọc
`.codex/constitution.md`, `.codex/context/lab04-cpg.md`, `README.md` mục
SDD Task Intake, `openspec/README.md`, spec mảng của tôi trong
`openspec/specs/.../spec.md`, task checklist trong
`openspec/changes/stage2-team-handoff/tasks.md`, và tracker của tôi trong
`docs/team/...`.

Sau đó kiểm tra `git status --short`, chạy baseline checks, rồi mới implement
thay đổi nhỏ nhất. Không đổi schema contract nếu chưa có Trí approve."

Sau khi AI làm xong, bắt AI báo lại:
- File đã sửa
- Command đã chạy
- Pass/fail
- Evidence đã có
- Blocker còn lại
````

## Tin 10 - Điều Kiện Tick Done

````md
Một task chỉ được tick done khi có đủ:

1. Đã đọc đúng OpenSpec/spec/task file.
2. Đã chạy baseline checks.
3. Đã attach evidence hoặc ghi blocker rõ ràng.
4. PR vào `dev` không đổi schema contract ngoài phạm vi được giao.

Nếu thiếu evidence thì chưa tick done.
````
