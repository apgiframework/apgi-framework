"""CI gates XC-CI-01.x: registries, bundle, scans, power, manifests, gate table."""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys

import jsonschema
import pytest
import yaml

from apgi.spec_bundle import BundleVerificationError, verify_bundle

ROOT = pathlib.Path(__file__).resolve().parent.parent


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def test_generated_registries_up_to_date():
    """S1-PR2b-02: generated files are never hand-edited; drift fails."""
    result = run("scripts/build_specifications.py", "--check")
    assert result.returncode == 0, result.stderr


def test_spec_bundle_verifies_and_is_current():
    """S1-FWK-04 / XC-CI-01.2."""
    result = run("scripts/build_spec_bundle.py", "--check")
    assert result.returncode == 0, result.stderr
    assert verify_bundle(ROOT)["file_count"] > 40


def test_consumer_rejects_altered_bundle(tmp_path):
    for top in ("bundle", "protocols", "specifications", "fixtures", "traceability", "gates", "releases"):
        shutil.copytree(ROOT / top, tmp_path / top, ignore=shutil.ignore_patterns("__pycache__"))
    verify_bundle(tmp_path)
    reg = tmp_path / "specifications/model/parameter-registry.yaml"
    reg.write_text(reg.read_text().replace("default: 0.60", "default: 0.61", 1))
    with pytest.raises(BundleVerificationError, match="checksum mismatch"):
        verify_bundle(tmp_path)
    reg.write_text((ROOT / "specifications/model/parameter-registry.yaml").read_text())
    (tmp_path / "gates" / "rogue.yaml").write_text("x: 1\n")
    with pytest.raises(BundleVerificationError, match="unlisted"):
        verify_bundle(tmp_path)


def test_gate_table_schema_valid():
    """S1-PR2b-01 / XC-CI-01.4."""
    schema = json.loads((ROOT / "gates/gate-table.schema.json").read_text())
    table = yaml.safe_load((ROOT / "gates/gate-table.yaml").read_text())
    jsonschema.validate(table, schema)
    status = {g["field"]: g["status"] for g in table["gates"]}
    assert status["Pi_i"] == status["beta"] == "not_testable_v0_1"
    assert {status[k] for k in ("S_t", "theta_t", "Pi_e")} == {"pending_K7"}
    exposed = yaml.safe_load((ROOT / "gates/exposable-fields.yaml").read_text())["fields"]
    assert not any(f["field"] in {"Pi_i", "beta", "S_t", "theta_t", "Pi_e"} for f in exposed)


def test_fixture_files_validate_against_schema():
    schema = json.loads((ROOT / "fixtures/fixture.schema.json").read_text())
    for path in sorted((ROOT / "fixtures").glob("*.json")):
        if path.name in {"INDEX.json", "fixture.schema.json"}:
            continue
        jsonschema.validate(json.loads(path.read_text()), schema)


def test_release_manifest_builds_and_validates(tmp_path):
    """S1-FWK-10: every release manifest validates against the schema."""
    out = tmp_path / "release-manifest.json"
    result = run("scripts/build_release_manifest.py", "--out", str(out))
    assert result.returncode == 0, result.stderr
    manifest = json.loads(out.read_text())
    assert manifest["certification"]["status"] == "Not certified"
    bad = dict(manifest, source_commit="not-a-sha")
    schema = json.loads((ROOT / "releases/release-manifest.schema.json").read_text())
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_notation_scan_zero_findings():
    """SCI-004: zero-findings scan."""
    result = run("scripts/scan_notation.py")
    assert result.returncode == 0, result.stderr


def test_terminology_scan_zero_findings():
    """SCI-006."""
    result = run("scripts/scan_terminology.py")
    assert result.returncode == 0, result.stderr


def test_terminology_scan_detects_forbidden_expansion(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import scan_terminology

    bad = tmp_path / "bad.md"
    bad.write_text("APGI (Adaptive Predictive Global Integration) is wrong.")
    original = scan_terminology.ROOT
    scan_terminology.ROOT = tmp_path
    try:
        result = scan_terminology.scan(["bad.md"])
    finally:
        scan_terminology.ROOT = original
    assert len(result["findings"]) >= 1


def test_power_reproduction_all_mismatches_acknowledged(tmp_path):
    """REP-003: independent scipy recomputation; non-matches must be tracked."""
    out = tmp_path / "power.json"
    result = run("scripts/verify_power.py", "--report", str(out))
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    by_case = {c["case"]: c for c in report["cases"]}
    assert by_case["PWR-P00-N"]["status"] == "match"
    assert by_case["PWR-P05-N"]["n_reference"] == 44
    assert by_case["PWR-P03-N"]["status"] == "mismatch"  # DEV-0004
    assert report["unacknowledged"] == []


def test_parameter_registry_ids_unique_and_complete():
    """S1-FWK-03 / SCI-005: stable unique IDs; every default labelled."""
    reg = yaml.safe_load((ROOT / "specifications/model/parameter-registry.yaml").read_text())
    ids = [e["id"] for e in reg["entries"]]
    assert len(ids) == len(set(ids))
    for e in reg["entries"]:
        assert e["provenance"]["category"] in {"analytically_derived", "post_hoc_calibrated", "assumed"}
        assert e["scope_layer"] in {"computational", "information_theoretic", "thermodynamic"}
        assert e["provenance"]["source"]
    by_id = {e["id"]: e for e in reg["entries"]}
    kappa = by_id["PAR-KAPPA"]
    assert kappa["scope_layer"] == "thermodynamic" and kappa["default"] is None
    assert kappa["control"] == "uncalibrated" and "PAR-GAMMA-SIG" in kappa["must_not_alias"]
    assert by_id["PAR-THETA-0"]["provenance"]["category"] == "post_hoc_calibrated"
    assert by_id["STA-THETA-T"]["role"] == "state" and by_id["PAR-THETA-0"]["role"] == "parameter"
    assert by_id["PAR-PI-E"]["kind"] == "precision" and by_id["SIG-Z-E"]["kind"] == "prediction_error"


def test_code_defaults_match_registry():
    from apgi import core, precision

    reg = {e["id"]: e for e in yaml.safe_load((ROOT / "specifications/model/parameter-registry.yaml").read_text())["entries"]}
    pairs = {"PAR-THETA-0": core.THETA_0_DEFAULT, "PAR-LAMBDA-THETA": core.LAMBDA_THETA_DEFAULT,
             "PAR-KAPPA-META": core.KAPPA_META_DEFAULT, "PAR-DELTA-INFO": core.DELTA_INFO_DEFAULT,
             "PAR-ETA-NE": core.ETA_NE_DEFAULT, "PAR-GAMMA-SIG": core.GAMMA_SIG_DEFAULT,
             "PAR-TAU-S": core.TAU_S_DEFAULT, "PAR-BETA-SM": core.BETA_SM_DEFAULT,
             "PAR-DELTA-RESET": core.DELTA_RESET_DEFAULT, "PAR-RHO-RETAIN": core.RHO_RETAIN_DEFAULT,
             "PAR-GAMMA-NE": core.GAMMA_NE_DEFAULT, "CON-NE-SUBDOMINANCE": core.NE_SUBDOMINANCE_LIMIT,
             "CON-PI-MIN": core.PI_MIN, "CON-PI-MAX": core.PI_MAX,
             "PAR-ALPHA-EMA": precision.ALPHA_EMA_DEFAULT, "CON-EPS-STAB": precision.EPS_STAB_DEFAULT}
    for rid, value in pairs.items():
        assert reg[rid]["default"] == value, rid


def test_every_prediction_traces_to_equation_code_protocol_evidence():
    """S1-FWK-06 acceptance: every prediction maps to equation, code, protocol and evidence."""
    preds = yaml.safe_load((ROOT / "traceability/predictions.yaml").read_text())["predictions"]
    evidence = {e["id"] for e in yaml.safe_load((ROOT / "traceability/evidence-map.yaml").read_text())["evidence"]}
    claims = {c["id"] for c in yaml.safe_load((ROOT / "specifications/claims/claim-register.yaml").read_text())["claims"]}
    rules = {r["id"] for r in yaml.safe_load((ROOT / "specifications/model/decision-rule-registry.yaml").read_text())["entries"]}
    assert len(preds) == 40
    for p in preds:
        assert p["equations"] and p["code"] and p["protocol_file"]
        assert p["evidence"] in evidence and p["claim"] in claims and p["decision_rule"] in rules


def test_claim_register_labels():
    claims = yaml.safe_load((ROOT / "specifications/claims/claim-register.yaml").read_text())["claims"]
    assert all(c["id"].startswith("CLM-") for c in claims)
    assert {c["status"] for c in claims} <= {"established", "derived", "calibrated", "speculative"}
    assert {c["epistemic_tier"] for c in claims} <= {"thermodynamic", "information_theoretic", "computational"}
    assert next(c for c in claims if c["id"] == "CLM-0009")["status"] == "speculative"
