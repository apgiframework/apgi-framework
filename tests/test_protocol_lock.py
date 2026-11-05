"""TC-REP-01 / TC-PRO-02: lock-verified protocol loading refuses altered input."""

from __future__ import annotations

import json
import logging
import pathlib
import shutil

import pytest

from apgi.protocols import (
    EXPECTED_PROTOCOL_IDS,
    ProtocolLockError,
    ProtocolValidationError,
    decision_rule_hash,
    load_protocol,
    load_protocols,
    verify_lock,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture
def protocol_copy(tmp_path):
    dest = tmp_path / "protocols"
    shutil.copytree(ROOT / "protocols", dest)
    return dest


def _rehash(folder: pathlib.Path) -> None:
    import hashlib

    manifest = json.loads((folder / "MANIFEST.json").read_text())
    for entry in manifest["files"]:
        entry["sha256"] = hashlib.sha256((folder / entry["path"]).read_bytes()).hexdigest()
    (folder / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))


def test_untouched_set_verifies_and_loads():
    lock = verify_lock(ROOT / "protocols")
    assert lock["release"] == "1.1.0"
    protocols = load_protocols(ROOT / "protocols")
    assert tuple(protocols) == EXPECTED_PROTOCOL_IDS


def test_single_altered_file_refuses_and_produces_no_output(protocol_copy, tmp_path):
    target = protocol_copy / "protocol_3_anticipation_fmri.json"
    target.write_bytes(target.read_bytes().replace(b'"alpha": 0.05', b'"alpha": 0.10', 1))
    out_dir = tmp_path / "outputs"

    def pipeline():
        protocols = load_protocols(protocol_copy)  # must raise before any output
        out_dir.mkdir()
        (out_dir / "result.json").write_text(json.dumps(list(protocols)))

    with pytest.raises(ProtocolLockError, match="sha256 mismatch: protocol_3"):
        pipeline()
    assert not out_dir.exists()


@pytest.mark.parametrize("mutation", ["delete", "extra", "manifest_release"])
def test_missing_extra_or_wrong_release_refused(protocol_copy, mutation):
    if mutation == "delete":
        (protocol_copy / "protocol_0_hep_proxy_validation.json").unlink()
    elif mutation == "extra":
        shutil.copy(protocol_copy / "protocol_1_cardiac_eeg.json", protocol_copy / "protocol_8_extra.json")
    else:
        manifest = json.loads((protocol_copy / "MANIFEST.json").read_text())
        manifest["release"] = "9.9.9"
        (protocol_copy / "MANIFEST.json").write_text(json.dumps(manifest))
    with pytest.raises(ProtocolLockError):
        load_protocols(protocol_copy)


def test_schema_change_is_covered_by_lock(protocol_copy):
    schema = protocol_copy / "schemas" / "protocol.schema.json"
    schema.write_text(schema.read_text() + " ")
    with pytest.raises(ProtocolLockError):
        load_protocols(protocol_copy)


@pytest.mark.parametrize("payload,match", [
    (b'{"protocol_id": "APGI-P01", "protocol_id": "APGI-P01"}', "duplicate JSON key"),
    (b'{"x": NaN}', "non-finite"),
    (b'{"x": 1e999}', "non-finite"),
    (b'{"protocol_id": ', "malformed JSON"),
    (b'{"protocol_id": "APGI-P01"}', "required property"),
])
def test_malformed_or_incomplete_definitions_rejected_atomically(protocol_copy, payload, match):
    """Even with a re-signed manifest, invalid content is rejected and nothing returned."""
    (protocol_copy / "protocol_1_cardiac_eeg.json").write_bytes(payload)
    _rehash(protocol_copy)
    with pytest.raises(ProtocolValidationError, match=match):
        load_protocols(protocol_copy)


def test_incompatible_version_rejected(protocol_copy):
    path = protocol_copy / "protocol_2_somatic_agent_sim.json"
    data = json.loads(path.read_text())
    data["version"] = "1.2.0"
    path.write_text(json.dumps(data))
    _rehash(protocol_copy)
    with pytest.raises(ProtocolValidationError):
        load_protocols(protocol_copy)


def test_loaded_definitions_are_immutable():
    """VAL-001: a registered rule cannot be altered in memory after loading."""
    proto = load_protocol("APGI-P01", ROOT / "protocols")
    with pytest.raises(TypeError):
        proto["sub_predictions"][0]["status"] = "exploratory"  # type: ignore[index]
    with pytest.raises(TypeError):
        proto["power_analysis"]["alpha"] = 0.5  # type: ignore[index]


def test_decision_rule_hash_matches_registry():
    import yaml

    registry = yaml.safe_load((ROOT / "specifications/model/decision-rule-registry.yaml").read_text())
    proto = load_protocol("APGI-P01", ROOT / "protocols")
    entry = next(e for e in registry["entries"] if e["id"] == "DR-P01-1A")
    assert decision_rule_hash(proto, "Pred 1.A") == entry["rule_sha256"]
    with pytest.raises(ProtocolValidationError):
        decision_rule_hash(proto, "Pred 9.Z")


def test_audit_events_emitted(protocol_copy, caplog):
    with caplog.at_level(logging.INFO, logger="apgi.protocols"):
        load_protocols(ROOT / "protocols")
        (protocol_copy / "VALIDATION.json").write_text("{}")
        with pytest.raises(ProtocolLockError):
            verify_lock(protocol_copy)
    events = [json.loads(r.message)["event"] for r in caplog.records]
    assert "protocol_lock_verified" in events and "protocols_loaded" in events
    assert "protocol_lock_failed" in events


def test_unknown_protocol_id():
    with pytest.raises(ProtocolValidationError):
        load_protocol("APGI-P99", ROOT / "protocols")
