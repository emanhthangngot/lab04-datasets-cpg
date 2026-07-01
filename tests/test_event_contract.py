import ast
import json
import re
from pathlib import Path

from parser_service.ast_extractor import extract_ast_nodes_gen
from parser_service.ids import make_edge_id, make_external_target_id
from parser_service.schemas import (
    build_edge_event,
    build_error_event,
    build_metadata_event,
    build_node_event,
)
from tests.conftest import DummyContext


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "cpg-events.schema.json"


def load_contract() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def resolve_ref(contract: dict, ref: str) -> dict:
    prefix = "#/$defs/"
    assert ref.startswith(prefix)
    return contract["$defs"][ref.removeprefix(prefix)]


def event_schema(contract: dict, name: str) -> dict:
    """Merge the simple allOf shape used by the contract for test validation."""

    raw = contract["$defs"][name]
    merged = {"required": [], "properties": {}, "additionalProperties": True}
    for part in raw.get("allOf", [raw]):
        if "$ref" in part:
            part = resolve_ref(contract, part["$ref"])
        merged["required"].extend(part.get("required", []))
        merged["properties"].update(part.get("properties", {}))
        if part.get("additionalProperties") is False:
            merged["additionalProperties"] = False
    merged["required"] = sorted(set(merged["required"]))
    return merged


def validate_event(contract: dict, name: str, event: dict) -> None:
    schema = event_schema(contract, name)
    missing = set(schema["required"]) - set(event)
    assert not missing, f"{name} missing required fields: {sorted(missing)}"

    if schema["additionalProperties"] is False:
        extra = set(event) - set(schema["properties"])
        assert not extra, f"{name} has fields outside schema: {sorted(extra)}"

    for field, field_schema in schema["properties"].items():
        if field not in event:
            continue
        if "$ref" in field_schema:
            field_schema = resolve_ref(contract, field_schema["$ref"])
        value = event[field]
        if "const" in field_schema:
            assert value == field_schema["const"]
        if "enum" in field_schema:
            assert value in field_schema["enum"]
        expected_type = field_schema.get("type")
        if expected_type:
            expected = expected_type if isinstance(expected_type, list) else [expected_type]
            assert json_type(value) in expected, f"{field} expected {expected}, got {value!r}"


def json_type(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    raise AssertionError(f"Unsupported JSON value {value!r}")


def test_event_builders_match_json_schema_contract(tmp_path: Path) -> None:
    contract = load_contract()
    context = DummyContext(repo_root=tmp_path)

    node = build_node_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        node_id="node",
        node_type="FunctionDef",
        scope_path="load_dataset",
        lineno=1,
        col_offset=0,
        end_lineno=2,
        end_col_offset=4,
        properties={"name": "load_dataset"},
    )
    edge = build_edge_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        edge_id="edge",
        source_id="source",
        target_id="target",
        edge_type="CFG_NEXT",
        properties={"scope_path": "load_dataset"},
    )
    metadata = build_metadata_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        source="x = 1\n",
        num_ast_nodes=1,
        num_cfg_edges=2,
        num_dfg_edges=3,
        num_call_edges=4,
        parse_duration_ms=5,
        status="success",
    )
    error = build_error_event(
        context=context,
        file_id="file",
        file_path="src/datasets/broken.py",
        error=SyntaxError("bad syntax", ("broken.py", 3, 5, "x =\n")),
    )

    validate_event(contract, "nodeEvent", node)
    validate_event(contract, "edgeEvent", edge)
    validate_event(contract, "metadataEvent", metadata)
    validate_event(contract, "errorEvent", error)


def test_error_event_status_is_failed(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    error = build_error_event(
        context=context,
        file_id="file",
        file_path="src/datasets/broken.py",
        error=SyntaxError("bad syntax"),
    )

    assert error["status"] == "failed"


def test_error_event_includes_zero_based_location(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    error = build_error_event(
        context=context,
        file_id="file",
        file_path="src/datasets/broken.py",
        error=SyntaxError("bad syntax", ("broken.py", 7, 4, "bad\n")),
    )

    validate_event(load_contract(), "errorEvent", error)
    assert error["lineno"] == 7
    assert error["col_offset"] == 3


def test_spark_metadata_schema_matches_json_schema_contract() -> None:
    contract = load_contract()
    metadata_fields = set(event_schema(contract, "metadataEvent")["properties"])
    spark_source = (ROOT / "spark_jobs" / "metadata_stream_to_mongo.py").read_text(
        encoding="utf-8"
    )
    spark_fields = set(re.findall(r'\.add\("([^"]+)"', spark_source))

    assert spark_fields == metadata_fields


def test_mongodb_writer_uses_connector_10_replace_options() -> None:
    spark_source = (ROOT / "spark_jobs" / "metadata_stream_to_mongo.py").read_text(
        encoding="utf-8"
    )

    assert 'option("spark.mongodb.write.operationType", "replace")' in spark_source
    assert 'option("spark.mongodb.write.idFieldList", "file_id")' in spark_source
    assert 'option("operationType", "replace")' not in spark_source
    assert 'option("idFieldList", "file_id")' not in spark_source


def test_neo4j_connector_references_only_schema_fields() -> None:
    contract = load_contract()
    connector = json.loads((ROOT / "neo4j" / "sink_connector.json").read_text(encoding="utf-8"))
    config = connector["config"]

    node_fields = set(event_schema(contract, "nodeEvent")["properties"])
    edge_fields = set(event_schema(contract, "edgeEvent")["properties"])

    node_refs = set(
        re.findall(r"event\.([A-Za-z_][A-Za-z0-9_]*)", config["neo4j.cypher.topic.cpg.nodes"])
    )
    edge_refs = set(
        re.findall(r"event\.([A-Za-z_][A-Za-z0-9_]*)", config["neo4j.cypher.topic.cpg.edges"])
    )

    assert node_refs <= node_fields
    assert edge_refs <= edge_fields


def test_neo4j_connector_uses_verified_sink_class() -> None:
    connector = json.loads((ROOT / "neo4j" / "sink_connector.json").read_text(encoding="utf-8"))

    assert (
        connector["config"]["connector.class"]
        == "org.neo4j.connectors.kafka.sink.Neo4jConnector"
    )


def test_runtime_config_locks_kraft_cluster_id_and_plugin_gate() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    plugin_script = (ROOT / "scripts" / "check_connect_plugins.sh").read_text(
        encoding="utf-8"
    )

    assert "CLUSTER_ID:" in compose
    assert "org.neo4j.connectors.kafka.sink.Neo4jConnector" in plugin_script
    assert 'plugin.get("type") == "sink"' in plugin_script


def test_unresolved_call_edges_use_external_placeholder_targets(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    target_id = make_external_target_id("numpy.array")
    edge = build_edge_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        edge_id=make_edge_id("call-node", target_id, "CALL_UNRESOLVED"),
        source_id="call-node",
        target_id=target_id,
        edge_type="CALL_UNRESOLVED",
        properties={"target_name": "numpy.array", "resolution": "unresolved"},
    )

    validate_event(load_contract(), "edgeEvent", edge)
    assert edge["target_id"] == "external:numpy.array"
    assert edge["properties"]["resolution"] == "unresolved"


def test_internal_edges_reference_emitted_node_ids(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    nodes = {"source", "target"}
    edge = build_edge_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        edge_id=make_edge_id("source", "target", "CFG_NEXT"),
        source_id="source",
        target_id="target",
        edge_type="CFG_NEXT",
    )

    assert edge["source_id"] in nodes
    assert edge["target_id"] in nodes


def test_ast_node_events_are_deterministic_except_event_time(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    source = "def load_dataset(x):\n    return x + 1\n"

    def normalized_events():
        tree = ast.parse(source)
        events = list(
            extract_ast_nodes_gen(
                tree=tree,
                file_id="file",
                file_path="src/datasets/config.py",
                context=context,
            )
        )
        for event in events:
            event.pop("event_time", None)
        return events

    assert normalized_events() == normalized_events()
