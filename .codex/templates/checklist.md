# Implementation Checklist — <NNN>-<short-slug>

## Preflight

- [ ] Read `.codex/constitution.md`.
- [ ] Read `.codex/context/lab04-cpg.md`.
- [ ] Read subsystem rule(s).
- [ ] Confirm affected Lab04 task and evidence target.

## Parser

- [ ] File discovery scope is correct.
- [ ] Stable IDs are deterministic.
- [ ] Events include required common fields.
- [ ] `properties` is always a map.
- [ ] `num_total_edges` is explicit.
- [ ] Producer flush behavior is preserved.

## Runtime

- [ ] Kafka topics are explicit.
- [ ] Docker Compose service context is used for CLIs.
- [ ] Neo4j connector class is verified.
- [ ] Spark submit includes Kafka and MongoDB packages.

## Stores

- [ ] Neo4j uses `MERGE` and safe constraints.
- [ ] MongoDB metadata writes are upsert/replace by `file_id`.
- [ ] Spark checkpoint is persistent.

## Replay

- [ ] Modified file reprocess uses new `run_id`.
- [ ] Connector lag is zero before cleanup.
- [ ] Duplicate node/edge/document checks are captured.

## Evidence

- [ ] Notebook outputs are executed.
- [ ] Screenshots are present and referenced.
- [ ] Jupyter Book builds.
- [ ] Public submission contains no secrets.
