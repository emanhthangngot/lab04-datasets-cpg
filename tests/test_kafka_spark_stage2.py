"""Stage 2 integration tests for Kafka/Spark runtime.

Owner: 23120180 - Tran Le Trung Truc
Spec: openspec/specs/kafka-spark/spec.md

These tests verify correctness of Kafka and Spark configurations without
requiring Docker or live services. They check:
- Sink connector JSON validity and required fields
- Connector config uses the locked Neo4j class
- Spark job schema matches parser metadata schema
- Topic names in init script match spec
- Evidence capture scripts exist
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent


# -----------------------------------------------------------------------
# Sink connector config tests
# -----------------------------------------------------------------------
class TestSinkConnectorConfig:
    """Verify neo4j/sink_connector.json correctness."""

    @pytest.fixture()
    def config(self) -> dict:
        path = PROJECT_ROOT / "neo4j" / "sink_connector.json"
        assert path.exists(), f"Missing {path}"
        return json.loads(path.read_text())

    def test_valid_json(self, config: dict) -> None:
        assert isinstance(config, dict)

    def test_has_name(self, config: dict) -> None:
        assert config.get("name") == "cpg-neo4j-sink"

    def test_has_config_section(self, config: dict) -> None:
        assert "config" in config
        assert isinstance(config["config"], dict)

    def test_connector_class_matches_spec(self, config: dict) -> None:
        """Spec: connector.class must be the verified Neo4j sink class."""
        expected = "org.neo4j.connectors.kafka.sink.Neo4jConnector"
        actual = config["config"].get("connector.class")
        assert actual == expected, f"connector.class is {actual!r}, expected {expected!r}"

    def test_topics_include_nodes_and_edges(self, config: dict) -> None:
        """Spec: Neo4j receives cpg.nodes and cpg.edges only."""
        topics = config["config"].get("topics", "")
        assert "cpg.nodes" in topics
        assert "cpg.edges" in topics
        assert "cpg.metadata" not in topics, "Neo4j must not receive metadata (Spark owns that)"

    def test_key_converter_is_string(self, config: dict) -> None:
        assert config["config"].get("key.converter") == (
            "org.apache.kafka.connect.storage.StringConverter"
        )

    def test_value_converter_schemas_disabled(self, config: dict) -> None:
        assert config["config"].get("value.converter.schemas.enable") == "false"

    def test_value_converter_is_string(self, config: dict) -> None:
        """Neo4j Kafka Connector 5.1.0 has a bug with JsonConverter + schemas.enable=false:
        it treats schemaless JSON payloads as tombstone (null), resulting in 0 nodes/edges.
        StringConverter bypasses this — the connector auto-parses JSON strings into Maps
        for __value, which works correctly (verified: 22,628 nodes, 7,968 edges)."""
        expected = "org.apache.kafka.connect.storage.StringConverter"
        actual = config["config"].get("value.converter", "")
        assert actual == expected, (
            f"value.converter is {actual!r}, expected {expected!r}. "
            f"Do NOT use JsonConverter — Neo4j Connector 5.1.0 bug causes 0 ingestion."
        )

    def test_no_duplicate_cypher_keys(self, config: dict) -> None:
        cfg_keys = list(config["config"].keys())
        assert "neo4j.cypher.topic.cpgnodes" not in cfg_keys
        assert "neo4j.topic.cypher.cpgnodes" not in cfg_keys

    def test_neo4j_uri_is_docker_internal(self, config: dict) -> None:
        uri = config["config"].get("neo4j.uri", "")
        assert "neo4j:" in uri, "URI should reference the Docker service name 'neo4j'"

    def test_cypher_nodes_uses_merge_and_coalesce(self, config: dict) -> None:
        """Spec: Cypher must use MERGE and coalesce(event.properties, {})."""
        cypher = config["config"].get("neo4j.cypher.topic.cpg.nodes", "")
        assert "MERGE" in cypher.upper()
        assert "coalesce(event.properties, {})" in cypher or "coalesce($event.properties, {})" in cypher

    def test_cypher_edges_uses_merge(self, config: dict) -> None:
        cypher = config["config"].get("neo4j.cypher.topic.cpg.edges", "")
        assert "MERGE" in cypher.upper()

    def test_cypher_nodes_sets_placeholder_false(self, config: dict) -> None:
        """Full node events must set placeholder = false."""
        cypher = config["config"].get("neo4j.cypher.topic.cpg.nodes", "")
        assert "placeholder = false" in cypher or "n.placeholder = false" in cypher

    def test_cypher_edges_creates_placeholder_endpoints(self, config: dict) -> None:
        """Edge Cypher must set placeholder = true on created endpoints."""
        cypher = config["config"].get("neo4j.cypher.topic.cpg.edges", "")
        assert "placeholder = true" in cypher or "a.placeholder = true" in cypher


# -----------------------------------------------------------------------
# Spark job schema tests
# -----------------------------------------------------------------------
class TestSparkJobSchema:
    """Verify spark_jobs/metadata_stream_to_mongo.py schema matches parser."""

    @pytest.fixture()
    def spark_source(self) -> str:
        path = PROJECT_ROOT / "spark_jobs" / "metadata_stream_to_mongo.py"
        assert path.exists()
        return path.read_text()

    def test_schema_fields_match_metadata_event(self, spark_source: str) -> None:
        """Spark schema must declare the same fields as build_metadata_event."""
        expected_fields = [
            "schema_version",
            "event_time",
            "repo",
            "commit_sha",
            "run_id",
            "file_id",
            "file_path",
            "file_size",
            "content_hash",
            "num_ast_nodes",
            "num_cfg_edges",
            "num_dfg_edges",
            "num_call_edges",
            "num_total_edges",
            "parse_duration_ms",
            "status",
        ]
        for field in expected_fields:
            assert f'"{field}"' in spark_source, f"Missing field {field!r} in Spark schema"

    def test_checkpoint_path_is_persistent(self, spark_source: str) -> None:
        """Spec: checkpoint path must be persistent under /mnt/checkpoints."""
        assert "/mnt/checkpoints/cpg_metadata" in spark_source

    def test_kafka_topic_is_metadata_only(self, spark_source: str) -> None:
        """Spec: Spark consumes only cpg.metadata."""
        assert "cpg.metadata" in spark_source
        # Spark must NOT consume nodes or edges
        ast.parse(spark_source)
        source_text = spark_source
        # Check that cpg.nodes and cpg.edges don't appear in subscribe options
        for line in source_text.splitlines():
            if "subscribe" in line and "cpg.nodes" in line:
                pytest.fail("Spark must not subscribe to cpg.nodes")
            if "subscribe" in line and "cpg.edges" in line:
                pytest.fail("Spark must not subscribe to cpg.edges")

    def test_mongodb_replace_upsert_by_file_id(self, spark_source: str) -> None:
        """Spec: MongoDB metadata is replaced by file_id."""
        assert "replace" in spark_source
        assert "file_id" in spark_source
        assert "upsertDocument" in spark_source

    def test_has_trigger_config(self, spark_source: str) -> None:
        """Spark job should have a trigger configuration."""
        assert "trigger" in spark_source or "processingTime" in spark_source

    def test_reads_from_earliest(self, spark_source: str) -> None:
        """Must read from earliest to pick up all metadata events."""
        assert "earliest" in spark_source


# -----------------------------------------------------------------------
# Kafka topic init script tests
# -----------------------------------------------------------------------
class TestKafkaTopicInit:
    """Verify scripts/init_kafka_topics.sh creates correct topics."""

    @pytest.fixture()
    def script_content(self) -> str:
        path = PROJECT_ROOT / "scripts" / "init_kafka_topics.sh"
        assert path.exists()
        return path.read_text()

    def test_creates_all_four_topics(self, script_content: str) -> None:
        """Spec: system SHALL create cpg.nodes, cpg.edges, cpg.metadata, cpg.errors."""
        for topic in ["cpg.nodes", "cpg.edges", "cpg.metadata", "cpg.errors"]:
            assert topic in script_content, f"Missing topic {topic!r} in init script"

    def test_uses_docker_compose_exec(self, script_content: str) -> None:
        """Spec: topic creation runs through Kafka service context."""
        assert "docker compose exec" in script_content

    def test_uses_if_not_exists(self, script_content: str) -> None:
        """Topics must be created idempotently."""
        assert "--if-not-exists" in script_content

    def test_nodes_and_edges_have_multiple_partitions(self, script_content: str) -> None:
        """cpg.nodes and cpg.edges should have multiple partitions."""
        import re
        assert re.search(r"create_topic\s+cpg\.nodes\s+4", script_content)
        assert re.search(r"create_topic\s+cpg\.edges\s+4", script_content)


# -----------------------------------------------------------------------
# Evidence capture scripts exist
# -----------------------------------------------------------------------
class TestEvidenceScriptsExist:
    """Verify evidence capture scripts are present."""

    @pytest.mark.parametrize(
        "script_name",
        [
            "capture_kafka_evidence.sh",
            "capture_connector_evidence.sh",
            "capture_spark_evidence.sh",
            "run_stage2_evidence.sh",
            "sanitize_evidence.sh",
        ],
    )
    def test_evidence_script_exists(self, script_name: str) -> None:
        path = PROJECT_ROOT / "scripts" / script_name
        assert path.exists(), f"Missing evidence script: {script_name}"

    @pytest.mark.parametrize(
        "script_name",
        [
            "capture_kafka_evidence.sh",
            "capture_connector_evidence.sh",
            "capture_spark_evidence.sh",
            "run_stage2_evidence.sh",
            "sanitize_evidence.sh",
        ],
    )
    def test_evidence_script_has_shebang(self, script_name: str) -> None:
        path = PROJECT_ROOT / "scripts" / script_name
        content = path.read_text(encoding="utf-8")
        assert content.startswith("#!/"), f"{script_name} missing shebang line"

    @pytest.mark.parametrize(
        "script_name",
        [
            "capture_kafka_evidence.sh",
            "capture_connector_evidence.sh",
            "capture_spark_evidence.sh",
            "run_stage2_evidence.sh",
            "sanitize_evidence.sh",
        ],
    )
    def test_evidence_script_uses_set_euo(self, script_name: str) -> None:
        """All scripts should use strict mode."""
        path = PROJECT_ROOT / "scripts" / script_name
        content = path.read_text(encoding="utf-8")
        assert "set -euo pipefail" in content, f"{script_name} missing strict mode"


# -----------------------------------------------------------------------
# Docker Compose configuration tests
# -----------------------------------------------------------------------
class TestDockerCompose:
    """Verify docker-compose.yml has correct service configuration."""

    @pytest.fixture()
    def compose_content(self) -> str:
        path = PROJECT_ROOT / "docker-compose.yml"
        assert path.exists()
        return path.read_text(encoding="utf-8")

    def test_spark_image_is_bitnamilegacy(self, compose_content: str) -> None:
        """Spec: Spark container uses bitnamilegacy/spark:3.5.0."""
        assert "bitnamilegacy/spark:3.5.0" in compose_content

    def test_spark_mode_is_master(self, compose_content: str) -> None:
        """Spec: SPARK_MODE=master so container stays available for exec."""
        assert "SPARK_MODE: master" in compose_content or "SPARK_MODE=master" in compose_content

    def test_spark_mounts_checkpoints(self, compose_content: str) -> None:
        """Checkpoint volume must be mounted."""
        assert "spark-checkpoints" in compose_content
        assert "/mnt/checkpoints" in compose_content

    def test_spark_checkpoint_volume_is_initialized_for_non_root_user(
        self, compose_content: str
    ) -> None:
        """Spark UID 1001 must be able to create its checkpoint directory."""
        assert "spark-checkpoint-init:" in compose_content
        assert "chown -R 1001:0 /mnt/checkpoints" in compose_content
        assert "service_completed_successfully" in compose_content

    def test_kafka_auto_create_disabled(self, compose_content: str) -> None:
        """Spec: do not rely on auto-create topics."""
        assert "KAFKA_AUTO_CREATE_TOPICS_ENABLE" in compose_content
        # Ensure it contains false for auto-create setting
        assert re.search(r"KAFKA_AUTO_CREATE_TOPICS_ENABLE:\s*['\"]?false['\"]?", compose_content)

    def test_parser_service_exists(self, compose_content: str) -> None:
        """Parser service must exist for docker compose run."""
        assert "parser:" in compose_content


# -----------------------------------------------------------------------
# Stage 2 remediation contracts
# -----------------------------------------------------------------------
def test_runbook_requires_neo4j_password_without_literal_password() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    assert "NEO4J_PASSWORD" in source
    assert "cypher-shell -u neo4j -p password" not in source


def test_runbook_keeps_shared_graph_store_checks() -> None:
    runbook = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    source = (PROJECT_ROOT / "scripts" / "capture_store_evidence.sh").read_text()
    assert "bash scripts/capture_store_evidence.sh" in runbook
    for marker in ["node_count", "non_placeholder_count", "edge_count", "duplicate_nodes", "duplicate_edges", "file_metadata"]:
        assert marker in source
    assert 'distinct("file_id")' in source
    assert 'distinct("file_path")' in source
    assert 'distinct("repo")' in source


def test_tracker_has_one_verified_test_count_and_cross_owner_gate() -> None:
    source = (PROJECT_ROOT / "docs" / "team" / "kafka-spark.md").read_text()
    assert "65 tests" not in source
    assert "Final count recorded after remediation tests" in source or "tests passed" in source
    assert "Thanh" in source and "recheck" in source


def test_kafka_capture_has_fail_fast_contract() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_kafka_evidence.sh").read_text()
    assert "sys.exit(1)" in source
    assert "status" in source and "failed" in source
    assert "properties" in source


def test_spark_batch_is_persisted_and_released() -> None:
    source = (PROJECT_ROOT / "spark_jobs" / "metadata_stream_to_mongo.py").read_text()
    assert ".persist(" in source
    assert ".unpersist(" in source


def test_spark_metadata_test_has_no_unused_ast_assignment() -> None:
    source = (PROJECT_ROOT / "tests" / "test_kafka_spark_stage2.py").read_text()
    assert not re.search(r"^\s*tree = ast\.parse", source, re.MULTILINE)


def test_spark_evidence_fails_when_stream_or_metadata_is_missing() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_spark_evidence.sh").read_text()
    assert "metadata_stream_to_mongo.py" in source
    assert "Spark metadata stream is not running" in source
    assert "Spark did not commit and catch up" in source
    assert "checkpoint directory disappeared after a committed batch" in source
    assert "file_metadata count is" in source
    assert "MONGO_COUNT" in source


def test_runbook_propagates_spark_evidence_failure() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    assert 'wait "$SPARK_PID"' in source
    assert "|| true" not in source[source.index("SPARK_PID=$!") : source.index("# --------------------------------------------------------------------------\n# Summary")]


def test_connector_template_does_not_commit_neo4j_password() -> None:
    connector = json.loads(
        (PROJECT_ROOT / "neo4j" / "sink_connector.json").read_text(encoding="utf-8")
    )
    assert "neo4j.authentication.basic.password" not in connector["config"]


def test_registration_injects_neo4j_password_from_environment() -> None:
    source = (PROJECT_ROOT / "scripts" / "register_neo4j_sink.sh").read_text()
    assert "NEO4J_PASSWORD:?" in source
    assert 'os.environ["NEO4J_PASSWORD"]' in source
    assert 'config["neo4j.authentication.basic.password"]' in source


def test_spark_evidence_requires_committed_checkpoint_offset() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_spark_evidence.sh").read_text()
    offsets_block = source[
        source.index('echo "--- Committed offsets ---"') : source.index(
            "# --------------------------------------------------------------------------\n# 5."
        )
    ]
    assert "exit 1" in offsets_block
    assert "no committed offsets yet" not in offsets_block


def test_spark_evidence_captures_latest_committed_checkpoint_offset() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_spark_evidence.sh").read_text()
    assert 'LATEST_OFFSET' in source
    assert 'sort -n' in source
    assert 'cat "$CHECKPOINT_PATH/offsets/$LATEST_OFFSET"' in source
    assert 'cat "$CHECKPOINT_PATH/offsets/0"' not in source


def test_tracker_keeps_graph_store_acceptance_pending_after_runtime_passes() -> None:
    source = (PROJECT_ROOT / "docs" / "team" / "kafka-spark.md").read_text()
    assert "Status: Stage 2 complete." not in source
    assert "Thanh acceptance pending" in source


def test_stage2_runbook_locks_parser_repository_identity() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    assert 'EXPECTED_REPO_NAME="huggingface/datasets"' in source
    assert 'REPO_NAME="$EXPECTED_REPO_NAME"' in source
    assert "printenv REPO_NAME" in source


def test_stage2_runbook_propagates_dataset_commit_sha() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    assert 'DATASET_COMMIT_SHA="$(git -C data/datasets rev-parse HEAD)"' in source
    assert 'export EXPECTED_COMMIT_SHA="$DATASET_COMMIT_SHA"' in source
    assert source.count('-e COMMIT_SHA="$DATASET_COMMIT_SHA"') == 2


def test_kafka_evidence_rejects_unknown_or_mixed_commit_sha() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_kafka_evidence.sh").read_text()
    assert 'EXPECTED_COMMIT_SHA:?' in source
    assert 'msg.get("commit_sha")' in source
    assert '"unknown"' in source
    assert "unexpected commit_sha values" in source


def test_connector_wait_validates_all_graph_event_commit_shas() -> None:
    source = (PROJECT_ROOT / "scripts" / "wait_neo4j_connector_idle.sh").read_text()
    assert "EXPECTED_COMMIT_SHA" in source
    assert 'event.get("commit_sha")' in source
    assert "unexpected commit_sha values" in source


def test_stage2_runbook_waits_for_connect_api() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    assert "CONNECT_WAIT_SECONDS" in source
    assert 'curl -fsS "$CONNECT_URL/connector-plugins"' in source
    assert "Kafka Connect API is ready" in source


def test_stage2_runbook_requires_clean_docker_reset() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    assert "Set RESET_DOCKER_STATE=1" in source
    assert 'COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-lab04-datasets-cpg}"' in source
    assert "docker compose down -v --remove-orphans" in source
    assert "before starting Stage 2" in source


def test_run_checks_prefers_python_with_pytest() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_checks.sh").read_text()
    assert '".venv/bin/python"' in source
    assert 'python3 -m pytest' not in source


def test_parser_is_manual_and_runbook_does_not_auto_start_it() -> None:
    compose_source = (PROJECT_ROOT / "docker-compose.yml").read_text()
    runbook_source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()

    parser_block = compose_source[compose_source.index("  parser:") : compose_source.index("\nvolumes:")]
    assert 'profiles: ["manual"]' in parser_block
    assert "docker compose up -d broker neo4j mongo connect spark" in runbook_source
    assert "docker compose up -d\n" not in runbook_source


def test_spark_evidence_requires_commit_and_kafka_catchup() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_spark_evidence.sh").read_text()
    assert "$CHECKPOINT_PATH/commits" in source
    assert "checkpoint_commits.txt" in source
    assert "KAFKA_END_OFFSET" in source
    assert 'CHECKPOINT_KAFKA_OFFSET" = "$KAFKA_END_OFFSET' in source
    assert "MSYS_NO_PATHCONV=1 docker compose" in source
    assert "Spark metadata stream is already running; reusing it" in source
    assert "--driver-memory 512m" in source
    assert "spark_stream.log" in source
    assert "pgrep -f '[m]etadata_stream_to_mongo.py'" in source
    assert "pgrep -f 'metadata_stream_to_mongo.py'" not in source
    assert "SPARK_MONGO_WAIT_SECONDS" in source
    assert "EXPECTED_MONGO_COUNT" in source


def test_connector_wait_requires_persisted_graph_counts() -> None:
    source = (PROJECT_ROOT / "scripts" / "wait_neo4j_connector_idle.sh").read_text()
    assert "NEO4J_STORE_WAIT_SECONDS" in source
    assert "topic_id_counts cpg.nodes" in source and "topic_id_counts cpg.edges" in source
    assert "duplicate emitted IDs detected" in source
    assert "coalesce(n.placeholder, false) = false" in source
    assert "Neo4j persisted graph matches unique emitted Kafka IDs" in source
