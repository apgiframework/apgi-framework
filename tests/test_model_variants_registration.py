"""S1-FWK-09, S1-PR2-01/03, REP-004 (TC-REP-04), DAT-004 dataset provenance."""

from __future__ import annotations

import pathlib

import numpy as np
import pytest
import yaml

from apgi import datasets
from apgi.model_variants import (
    VARIANTS,
    UnmappedParameterError,
    UnregisteredVariantError,
    label_for,
    map_parameters,
    require_variant,
)
from apgi.protocols import load_protocol, verify_lock
from apgi.registration import check_analysis, label_output

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_python_registry_matches_variant_files():
    files = {p.stem: yaml.safe_load(p.read_text()) for p in (ROOT / "specifications/model-variants").glob("MV-*.yaml")}
    assert set(files) == set(VARIANTS)
    for vid, body in files.items():
        assert body["variant_id"] == vid
        assert body["status"] == VARIANTS[vid]["status"]
        assert body["model_version"] == VARIANTS[vid]["model_version"]


def test_exploratory_variants_are_labelled():
    assert label_for("MV-HIERARCHICAL-EXT-1")["analysis_label"] == "exploratory"
    assert label_for("MV-CORE-DISCRETE-1")["confirmatory_eligible"] is True
    with pytest.raises(UnregisteredVariantError):
        require_variant("MV-NOT-REGISTERED")


def test_parameter_mapping_converts_units_explicitly():
    out = map_parameters({"theta_0": 0.35, "tau_theta": 20.0, "tau_S": 0.3}, step_seconds=0.06)
    assert out["kwargs"]["lambda_theta"] == pytest.approx(0.003)
    assert out["kwargs"]["tau_S"] == pytest.approx(5.0)
    assert out["registry_ids"]["theta_0"] == "PAR-THETA-0"
    assert out["label"]["confirmatory_eligible"] is False  # different formulation
    with pytest.raises(ValueError):
        map_parameters({"tau_theta": 20.0})


def test_unmapped_parameters_raise_or_run_labelled():
    """S1-PR2-03: silent substitution is impossible."""
    with pytest.raises(UnmappedParameterError):
        map_parameters({"theta_0": 0.35, "eta": 0.1})
    with pytest.raises(UnmappedParameterError):
        map_parameters({"unknown_param": 1.0})
    out = map_parameters({"theta_0": 0.35, "eta": 0.1, "rho": 0.2}, allow_alternative=True)
    assert out["unmapped"] == ["eta", "rho"]
    assert out["label"]["model_variant"] == "MV-PROTOCOL-REDUCED-1"
    assert out["label"]["analysis_label"] == "exploratory"


PROTO = load_protocol("APGI-P01", ROOT / "protocols")
LOCK = verify_lock(ROOT / "protocols")
REGISTERED_PLAN = {"prediction_id": "Pred 1.A", "alpha": 0.0125, "n": 62,
                   "model_variant": "MV-PROTOCOL-REDUCED-1",
                   "steps": [{"name": "mixed-effects ordered contrast", "registered": True,
                              "source": "primary_analysis"}]}


def test_registered_plan_is_confirmatory():
    check = check_analysis(PROTO, REGISTERED_PLAN)
    assert check.deviations == ()
    assert check.analysis_label == "confirmatory"


def test_injected_unregistered_step_flags_and_propagates():
    plan = dict(REGISTERED_PLAN, steps=REGISTERED_PLAN["steps"] + [{"name": "outlier winsorising", "registered": False}])
    check = check_analysis(PROTO, plan)
    assert [d.field for d in check.deviations] == ["steps"]
    result = label_output({"estimate": 0.4, "analysis_label": "confirmatory"}, check, LOCK)
    assert result["analysis_label"] == "exploratory"
    assert result["registration"]["deviations"][0]["actual"] == "outlier winsorising"
    assert result["registration"]["protocol_manifest_sha256"] == LOCK["manifest_sha256"]
    import json

    exported = json.loads(json.dumps(result))  # survives serialisation/export
    assert exported["analysis_label"] == "exploratory"


@pytest.mark.parametrize("override,field", [
    ({"alpha": 0.05}, "alpha"), ({"n": 30}, "n"), ({"model_variant": "MV-CORE-DISCRETE-1"}, "model_variant"),
    ({"parameters": {"theta_0": 0.6}}, "parameters.theta_0"),
])
def test_other_deviations_detected(override, field):
    check = check_analysis(PROTO, {**REGISTERED_PLAN, **override})
    assert field in [d.field for d in check.deviations]
    assert check.analysis_label == "exploratory"


def test_non_confirmatory_prediction_is_exploratory_without_deviation():
    check = check_analysis(PROTO, {"prediction_id": "Pred 1.F"})
    assert check.deviations == () and check.analysis_label == "exploratory"


def test_unknown_prediction_is_a_deviation():
    check = check_analysis(PROTO, {"prediction_id": "Pred 1.Z"})
    assert check.deviations[0].field == "prediction_id"
    assert check.rule_sha256 is None


def test_sample_dataset_provenance():
    data = datasets.make_sample_doc_groups(n_per_group=2, n_trials=5, seed=3)
    prov = datasets.dataset_provenance("make_sample_doc_groups", data, n_per_group=2, n_trials=5, seed=3)
    again = datasets.dataset_provenance("make_sample_doc_groups",
                                        datasets.make_sample_doc_groups(n_per_group=2, n_trials=5, seed=3))
    assert prov["checksum"] == again["checksum"]
    assert prov["model_variant"] == "MV-SAMPLE-DOC-1" and prov["analysis_label"] == "exploratory"
    assert {"source", "version", "checksum", "license", "history"} <= set(prov)
    assert set(np.unique(data["group_labels"])) == {"VS_UWS", "MCS", "Controls"}
    with pytest.raises(KeyError):
        datasets.dataset_provenance("nope", data)
