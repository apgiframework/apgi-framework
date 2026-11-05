"""Golden-fixture conformance for MV-CORE-DISCRETE-1 (TC-SCI-01, TC-SCI-02).

Expected values come from fixtures/generate_fixtures.py, which computes them
independently in 60-digit decimal arithmetic without importing apgi.
Covers S1-FIX-01..10, S1-FIX-07.1-07.3, S1-FIX-07.6 and AUD-FIX-1000 (the
fixtures remain provisional until scientifically approved).
"""

from __future__ import annotations

import json
import math
import pathlib
import subprocess
import sys

import pytest

from apgi import core
from apgi.extensions.epistemic import landauer_minimum_energy
from apgi.model_variants import UnregisteredVariantError, require_variant

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIX = ROOT / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


def dec(value):
    if isinstance(value, str):
        return {"NaN": math.nan, "Infinity": math.inf, "-Infinity": -math.inf}[value]
    return value


def close(actual: float, expected: float, tol: dict) -> bool:
    return abs(actual - expected) <= tol["abs"] + tol["rel"] * abs(expected)


class StoredDraws:
    """Generator stand-in that replays stored uniform draws (S1-FIX-09)."""

    def __init__(self, draws):
        self._draws = list(draws)
        self._i = 0

    def random(self):
        value = self._draws[self._i]
        self._i += 1
        return value


FUNCTIONS = {
    "compute_S_t": core.compute_S_t,
    "ignition_probability": core.ignition_probability,
    "compute_pi_i_eff": core.compute_pi_i_eff,
    "accumulate_S_t": core.accumulate_S_t,
    "apply_ne_threshold_gain": core.apply_ne_threshold_gain,
    "theta_equilibrium": core.theta_equilibrium,
    "landauer_minimum_energy": landauer_minimum_energy,
    "step_theta": core.step_theta,
    "post_ignition_reset": core.post_ignition_reset,
    "ignition_decision_strict": core.ignition_decision_strict,
}

TRIAL_KEYS = ("pi_e", "z_e", "pi_i_baseline", "z_i", "M_hat", "C_t", "I_t", "theta_t",
              "beta_sm", "gamma_sig", "S_prev", "tau_S", "NE_t", "theta_0", "lambda_theta",
              "kappa_meta", "delta_info", "eta_NE", "delta_reset", "rho_retain")


def test_fixtures_are_reproducible_from_generator():
    """S1-FIX-10: committed fixtures equal a fresh independent regeneration."""
    result = subprocess.run([sys.executable, "-I", str(FIX / "generate_fixtures.py"), "--check"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_every_fixture_declares_tolerance_and_variant():
    """S1-FIX-08: absolute and relative tolerances live inside each fixture."""
    for path in sorted(FIX.glob("*.json")):
        if path.name in {"INDEX.json", "fixture.schema.json"}:
            continue
        body = json.loads(path.read_text(encoding="utf-8"))
        assert body["tolerance"]["default"]["abs"] == 1e-9
        assert body["tolerance"]["default"]["rel"] == 1e-7
        assert body["model_variant"] == "MV-CORE-DISCRETE-1"
        assert body["approval"]["status"] == "provisional_unapproved"


CORE_CASES = load("core-equations.json")["cases"]


@pytest.mark.parametrize("case", CORE_CASES, ids=[c["id"] for c in CORE_CASES])
def test_core_equation_cases(case):
    tol = load("core-equations.json")["tolerance"]["default"]
    actual = FUNCTIONS[case["function"]](**case["inputs"])
    assert close(actual, case["expected"], tol), (actual, case["expected"])


def test_sign_fixture_value():
    """S1-FIX-04: z_e = −0.8, z_i = −0.5 with Π_e = 1.2, Π_i_eff = 0.9 → 1.41."""
    assert core.compute_S_t(1.2, -0.8, 0.9, -0.5) == pytest.approx(1.41, abs=1e-12)
    assert core.compute_S_t(1.2, -0.8, 0.9, 0.5) == core.compute_S_t(1.2, 0.8, 0.9, -0.5)


INVALID = load("invalid-configurations.json")


@pytest.mark.parametrize("case", INVALID["must_raise"], ids=[c["id"] for c in INVALID["must_raise"]])
def test_invalid_configurations_raise(case):
    """S1-FIX-06.4 / PRO-002: invalid domains raise; nothing is silently clipped."""
    inputs = {k: dec(v) for k, v in case["inputs"].items()}
    with pytest.raises(ValueError):
        FUNCTIONS[case["function"]](**inputs)


@pytest.mark.parametrize("case", INVALID["valid_clamping"], ids=[c["id"] for c in INVALID["valid_clamping"]])
def test_valid_clamping_does_not_raise(case):
    assert FUNCTIONS[case["function"]](**case["inputs"]) == case["expected"]


BOUNDARY = load("ignition-boundary.json")


@pytest.mark.parametrize("case", BOUNDARY["cases"], ids=[c["id"] for c in BOUNDARY["cases"]])
def test_strict_ignition_boundary(case):
    """TC-SCI-02: equality never ignites; ±ulp classification exact under EQ-2D."""
    assert core.ignition_decision_strict(case["S_t"], case["theta_t"]) is case["expected_strict"]


def test_bit_identical_boundary_conflict_is_tracked():
    """DEV-0001: the legacy deterministic criterion ignites at S == θ (P == 0.5)."""
    assert core.ignition_criterion(0.6, 0.6) is True
    assert core.ignition_decision_strict(0.6, 0.6) is False


def _run_vector(inputs: dict) -> dict:
    kwargs = {k: inputs[k] for k in TRIAL_KEYS}
    return core.run_trial(**kwargs, rng=StoredDraws([inputs["u"]]))


GOLDEN = load("golden-vectors.json")
SINGLE = [v for v in GOLDEN["vectors"] if v["category"] != "invalid"]
INVALID_VECTORS = [v for v in GOLDEN["vectors"] if v["category"] == "invalid"]


def test_golden_vector_counts():
    """AUD-FIX-1000: >= 1000 vectors in the required category mix."""
    counts = GOLDEN["counts"]
    assert GOLDEN["total"] >= 1000
    assert counts["ordinary"] >= 200 and counts["near_threshold"] >= 200
    assert counts["edge"] + counts["invalid"] >= 150
    assert counts["precision"] >= 150 and counts["threshold_refractory"] >= 150
    assert counts["seeded_dynamic"] >= 150


def test_golden_single_step_vectors():
    tol = GOLDEN["tolerance"]
    failures = []
    for vec in SINGLE:
        out = _run_vector({k: dec(v) for k, v in vec["inputs"].items()})
        exp = vec["expected"]
        if out["ignition"] != exp["ignition"]:
            failures.append((vec["id"], "ignition"))
        for key, rule in (("S_t", tol["S_t"]), ("theta_next", tol["theta"])):
            if not close(out[key], exp[key], rule):
                failures.append((vec["id"], key, out[key], exp[key]))
        for key in ("pi_i_eff", "S_input", "ignition_prob", "S_next"):
            if not close(out[key], exp[key], tol["default"]):
                failures.append((vec["id"], key, out[key], exp[key]))
    assert not failures, failures[:10]


@pytest.mark.parametrize("vec", INVALID_VECTORS, ids=[v["id"] for v in INVALID_VECTORS])
def test_golden_invalid_vectors_raise(vec):
    with pytest.raises(ValueError):
        _run_vector({k: dec(v) for k, v in vec["inputs"].items()})


def _replay(traj: dict, draws: list[float]) -> dict:
    p = traj["parameters"]
    off = traj["noise"]["offset"]
    rng = StoredDraws(draws[off: off + len(traj["inputs"])])
    S, theta = traj["initial"]["S_prev"], traj["initial"]["theta_t"]
    out = {"S_t": [], "theta_next": [], "ignition": [], "S_next": []}
    for row in traj["inputs"]:
        r = core.run_trial(row["pi_e"], row["z_e"], row["pi_i_baseline"], row["z_i"], row["M_hat"],
                           row["C_t"], row["I_t"], theta, beta_sm=p["beta_sm"],
                           gamma_sig=p["gamma_sig"], S_prev=S, tau_S=p["tau_S"], NE_t=row["NE_t"],
                           theta_0=p["theta_0"], lambda_theta=p["lambda_theta"],
                           kappa_meta=p["kappa_meta"], delta_info=p["delta_info"],
                           eta_NE=p["eta_NE"], delta_reset=p["delta_reset"],
                           rho_retain=p["rho_retain"], rng=rng)
        out["S_t"].append(r["S_t"])
        out["theta_next"].append(r["theta_next"])
        out["ignition"].append(r["ignition"])
        out["S_next"].append(r["S_next"])
        S, theta = r["S_next"], r["theta_next"]
    return out


def test_golden_seeded_dynamic_trajectories():
    """S1-FIX-06.6 / 07.3: deterministic trajectories from stored noise draws."""
    draws = load("noise-draws.json")["draws"]
    tol = GOLDEN["tolerance"]
    for traj in GOLDEN["trajectories"]:
        out = _replay(traj, draws)
        assert out["ignition"] == traj["expected"]["ignition"], traj["id"]
        for a, e in zip(out["S_t"], traj["expected"]["S_t"]):
            assert close(a, e, tol["S_t"]), traj["id"]
        for a, e in zip(out["theta_next"], traj["expected"]["theta_next"]):
            assert close(a, e, tol["theta"]), traj["id"]


DYN = load("threshold-dynamics.json")


@pytest.mark.parametrize("traj", DYN["trajectories"], ids=[t["id"] for t in DYN["trajectories"]])
def test_threshold_dynamics_trajectories(traj):
    """S1-FIX-02, S1-FIX-06.1/06.2: sub/near-threshold, ignition and reset."""
    draws = load("noise-draws.json")["draws"]
    p = traj["parameters"]
    if "offset" in traj["noise"]:
        off = traj["noise"]["offset"]
        rng = StoredDraws(draws[off: off + len(traj["inputs"])])
    else:
        rng = StoredDraws([row["u"] for row in traj["inputs"]])
    S, theta = traj["initial"]["S_prev"], traj["initial"]["theta_t"]
    tol = DYN["tolerance"]
    for k, row in enumerate(traj["inputs"]):
        r = core.run_trial(row["pi_e"], row["z_e"], row["pi_i_baseline"], row["z_i"], row["M_hat"],
                           row["C_t"], row["I_t"], theta, S_prev=S, NE_t=row["NE_t"], rng=rng, **p)
        assert r["ignition"] == traj["expected"]["ignition"][k]
        assert close(r["S_t"], traj["expected"]["S_t"][k], tol["S_t"])
        assert close(r["theta_t"], traj["expected"]["theta_t"][k], tol["theta"])
        S, theta = r["S_next"], r["theta_next"]


def test_half_step_sensitivity():
    """S1-FIX-06.5: forward Euler converges at first order (half dt ≈ half error)."""
    hs = DYN["half_step"]
    inp, p = hs["inputs"], hs["parameters"]
    tol = DYN["tolerance"]
    for dt, key in ((1.0, "dt_1.0"), (0.5, "dt_0.5")):
        theta, traj = inp["theta_initial"], [inp["theta_initial"]]
        for _ in range(int(round(inp["horizon"] / dt))):
            theta = core.step_theta(theta, inp["C_t"], inp["I_t"], NE_t=0.0, dt=dt, **p)
            traj.append(theta)
        for a, e in zip(traj, hs["expected"][key]):
            assert close(a, e, tol["theta"])
    lo, hi = hs["acceptance"]["error_ratio_range"]
    assert lo <= hs["expected"]["error_ratio_half_over_full"] <= hi


def test_noise_draws_identical_for_every_consumer():
    """S1-FIX-09: draws are data with a fixed digest, not a seed."""
    import hashlib

    body = load("noise-draws.json")
    digest = hashlib.sha256(json.dumps(body["draws"]).encode()).hexdigest()
    index = json.loads((FIX / "INDEX.json").read_text())
    assert body["count"] == len(body["draws"]) == 4000
    assert all(0.0 <= x < 1.0 for x in body["draws"])
    assert index["files"]["noise-draws.json"]
    assert len(digest) == 64


def test_model_version_migration_rejected():
    """S1-FIX-07.6: fixtures for another model version are rejected, not reinterpreted."""
    body = load("core-equations.json")
    assert require_variant(body["model_variant"], body["model_version"])
    with pytest.raises(UnregisteredVariantError):
        require_variant(body["model_variant"], "2.0.0")
    with pytest.raises(UnregisteredVariantError):
        require_variant("MV-UNKNOWN-9")
