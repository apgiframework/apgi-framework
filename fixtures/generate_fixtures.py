"""Independent golden-fixture generator for the APGI core model (MV-CORE-DISCRETE-1).

Expected values are computed with Python's ``decimal`` module at 60
significant digits directly from the equations in
``specifications/model/equations.yaml``. This script deliberately does NOT
import ``apgi`` — the implementation under test never produces its own
expected outputs (APGI-VAL-SPEC-1.2 §1.2 "Golden vector").

Inputs are IEEE-754 doubles; each is converted to Decimal exactly, the
reference is evaluated in high precision, and the result is rounded once to
the nearest double for storage (``repr`` round-trips exactly).

Outputs (all deterministic for a given generator version):
    fixtures/core-equations.json         per-equation cases incl. sign fixtures
    fixtures/threshold-dynamics.json     trajectories, resets, half-step study
    fixtures/ignition-boundary.json      equality / ±1 ulp / 4-ulp band cases
    fixtures/invalid-configurations.json must-raise cases (no silent clipping)
    fixtures/noise-draws.json            versioned stored uniform draws
    fixtures/golden-vectors.json         >= 1000 single-step + trajectory vectors

Status: PROVISIONAL. Numerical conventions (update order, boundary rule,
band width, tolerances) await scientific-authority approval (AUD-REG-04,
AUD-FIX-1000); see each file's ``approval`` block.

Usage:
    python fixtures/generate_fixtures.py          # (re)write all fixtures
    python fixtures/generate_fixtures.py --check  # fail if files would change
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import random
import sys
from decimal import Decimal, getcontext

getcontext().prec = 60

HERE = pathlib.Path(__file__).resolve().parent
GENERATOR_VERSION = "1.0.0"
MODEL_VARIANT = "MV-CORE-DISCRETE-1"
MODEL_VERSION = "1.0.0"
NOISE_SEED = 20261105

TOLERANCE = {
    "default": {"abs": 1e-9, "rel": 1e-7, "rule": "|a-e| <= abs + rel*|e|  (§6.1)"},
    "S_t": {"abs": 1e-9, "rel": 0.0, "rule": "|a-e| <= 1e-9 (AUD-FIX-1000)"},
    "theta": {"abs": 1e-9, "rel": 0.0, "rule": "|a-e| <= 1e-9 (AUD-FIX-1000)"},
    "classification": "exact outside the boundary band",
    "boundary_band_ulp": 4,
}

APPROVAL = {
    "status": "provisional_unapproved",
    "approver": "Not appointed",
    "blocking_items": ["AUD-REG-04", "AUD-FIX-1000", "AUD-SPEC-CONFIRM-13"],
}

# Package defaults restated independently (registry values, not imported).
DEFAULTS = {
    "theta_0": 0.60, "lambda_theta": 0.30, "kappa_meta": 0.20, "delta_info": 0.15,
    "eta_NE": 0.10, "gamma_sig": 5.0, "tau_S": 5.0, "beta_sm": 0.60,
    "delta_reset": 0.20, "rho_retain": 0.30, "gamma_NE": 0.30,
    "PI_MIN": 0.01, "PI_MAX": 10.0, "k_B": 1.380649e-23, "T_body": 310.0,
}

D = Decimal
ONE = D(1)


def d(x: float) -> Decimal:
    return D(float(x))  # exact binary value of the double


def f(x: Decimal) -> float:
    return float(x)  # correctly rounded to nearest double


def enc(x: float) -> float | str:
    if math.isnan(x):
        return "NaN"
    if math.isinf(x):
        return "Infinity" if x > 0 else "-Infinity"
    return x


# ── reference equations (high precision) ───────────────────────────────────


def ref_pi_i_eff(pi_b: float, beta: float, m: float) -> Decimal:
    raw = d(pi_b) * (d(beta) * d(m)).exp()
    lo, hi = d(DEFAULTS["PI_MIN"]), d(DEFAULTS["PI_MAX"])
    return min(max(raw, lo), hi)


def ref_S_input(pi_e: float, z_e: float, pi_i_eff: Decimal, z_i: float) -> Decimal:
    return d(pi_e) * abs(d(z_e)) + pi_i_eff * abs(d(z_i))


def ref_accumulate(S_prev: Decimal, S_in: Decimal, tau_S: float, dt: float = 1.0) -> Decimal:
    lam = ONE - (-(d(dt) / d(tau_S))).exp()
    return (ONE - lam) * S_prev + lam * S_in


def ref_prob(S: Decimal, theta: Decimal, gamma: float) -> Decimal:
    x = -d(gamma) * (S - theta)
    if x > 5000:
        return D(0)
    return ONE / (ONE + x.exp())


def ref_step_theta(theta: Decimal, C: float, I_val: float, NE: float, fired: bool, p: dict,
                   dt: float = 1.0) -> Decimal:
    dtheta = (-d(p["lambda_theta"]) * (theta - d(p["theta_0"])) + d(p["kappa_meta"]) * d(C)
              - d(p["delta_info"]) * d(I_val) + d(p["eta_NE"]) * d(NE))
    nxt = theta + d(dt) * dtheta
    if fired:
        nxt += d(p["delta_reset"])
    return nxt


def ref_trial(v: dict) -> dict:
    """One step of MV-CORE-DISCRETE-1 with a stored uniform draw ``u``."""
    pie = ref_pi_i_eff(v["pi_i_baseline"], v["beta_sm"], v["M_hat"])
    s_in = ref_S_input(v["pi_e"], v["z_e"], pie, v["z_i"])
    s_t = ref_accumulate(d(v["S_prev"]), s_in, v["tau_S"])
    p = ref_prob(s_t, d(v["theta_t"]), v["gamma_sig"])
    fired = d(v["u"]) < p
    theta_next = ref_step_theta(d(v["theta_t"]), v["C_t"], v["I_t"], v["NE_t"], fired, v)
    s_next = d(v["rho_retain"]) * s_t if fired else s_t
    return {"pi_i_eff": f(pie), "S_input": f(s_in), "S_t": f(s_t), "ignition_prob": f(p),
            "ignition": bool(fired), "theta_next": f(theta_next), "S_next": f(s_next),
            "_margin": float(abs(d(v["u"]) - p))}


# ── input sampling helpers ────────────────────────────────────────────────


def base_params(rng: random.Random) -> dict:
    return {
        "pi_e": rng.uniform(0.5, 2.0), "z_e": rng.uniform(-2.0, 2.0),
        "pi_i_baseline": rng.uniform(0.5, 2.0), "z_i": rng.uniform(-2.0, 2.0),
        "M_hat": rng.uniform(-1.0, 1.0), "beta_sm": rng.uniform(0.1, 1.2),
        "C_t": rng.uniform(0.0, 2.0), "I_t": rng.uniform(0.0, 1.0), "NE_t": rng.uniform(0.0, 1.0),
        "theta_t": rng.uniform(0.25, 1.5), "S_prev": rng.uniform(0.0, 2.0),
        "tau_S": rng.uniform(1.0, 20.0), "gamma_sig": rng.uniform(2.0, 7.5),
        "theta_0": rng.uniform(0.25, 0.85), "lambda_theta": rng.uniform(0.1, 0.5),
        "kappa_meta": rng.uniform(0.001, 0.5), "delta_info": rng.uniform(0.0, 1.0),
        "eta_NE": rng.uniform(0.01, 0.5), "delta_reset": rng.uniform(0.0, 0.5),
        "rho_retain": rng.uniform(0.1, 0.5), "u": rng.random(),
    }


def settle_draw(v: dict, rng: random.Random) -> dict:
    """Redraw ``u`` until it is >= 1e-9 away from P (no ambiguous decisions)."""
    for _ in range(1000):
        if ref_trial(v)["_margin"] >= 1e-9:
            return v
        v["u"] = rng.random()
    raise RuntimeError("could not find an unambiguous draw")


def vector(category: str, idx: int, v: dict) -> dict:
    exp = ref_trial(v)
    exp.pop("_margin")
    return {"id": f"GV-{category[:3].upper()}-{idx:04d}", "category": category,
            "inputs": {k: enc(x) for k, x in v.items()}, "expected": exp}


def invalid_vector(idx: int, v: dict, field: str, value: float, reason: str) -> dict:
    w = dict(v)
    w[field] = value
    return {"id": f"GV-INV-{idx:04d}", "category": "invalid", "inputs": {k: enc(x) for k, x in w.items()},
            "expected": {"raises": "ValueError", "field": field, "reason": reason}}


# ── fixture builders ───────────────────────────────────────────────────────


def core_equations() -> dict:
    cases = []
    # EQ-1 sign fixtures (S1-FIX-04): declared gains Π_e = 1.2, Π_i_eff = 0.9
    for cid, ze, zi in [("EQ1-SIGN-NEG", -0.8, -0.5), ("EQ1-SIGN-POS", 0.8, 0.5),
                        ("EQ1-SIGN-MIXED-A", -0.8, 0.5), ("EQ1-SIGN-MIXED-B", 0.8, -0.5),
                        ("EQ1-ZERO", 0.0, 0.0)]:
        cases.append({"id": cid, "equation": "EQ-1", "function": "compute_S_t",
                      "inputs": {"pi_e": 1.2, "z_e": ze, "pi_i_eff": 0.9, "z_i": zi},
                      "expected": f(ref_S_input(1.2, ze, d(0.9), zi))})
    for cid, pe, ze, pi, zi in [("EQ1-EXTERO-ONLY", 2.0, 3.0, 0.0, 99.0),
                                ("EQ1-INTERO-ONLY", 0.0, 99.0, 1.5, 4.0),
                                ("EQ1-LARGE", 10.0, 1e6, 10.0, -1e6)]:
        cases.append({"id": cid, "equation": "EQ-1", "function": "compute_S_t",
                      "inputs": {"pi_e": pe, "z_e": ze, "pi_i_eff": pi, "z_i": zi},
                      "expected": f(ref_S_input(pe, ze, d(pi), zi))})
    for cid, s, th, g in [("EQ2-AT-THRESHOLD", 0.6, 0.6, 5.0), ("EQ2-ABOVE", 1.0, 0.6, 5.0),
                          ("EQ2-BELOW", 0.2, 0.6, 5.0), ("EQ2-STEEP", 0.61, 0.6, 7.5),
                          ("EQ2-SATURATE-HIGH", 50.0, 0.6, 7.5), ("EQ2-SATURATE-LOW", 0.0, 50.0, 7.5)]:
        cases.append({"id": cid, "equation": "EQ-2", "function": "ignition_probability",
                      "inputs": {"S_t": s, "theta_t": th, "gamma_sig": g},
                      "expected": f(ref_prob(d(s), d(th), g))})
    for cid, pb, b, m in [("EQ4-NEUTRAL", 1.0, 0.6, 0.0), ("EQ4-UP", 1.0, 0.6, 1.5),
                          ("EQ4-DOWN", 1.0, 0.6, -1.5), ("EQ4-CLAMP-HIGH", 5.0, 1.2, 2.0),
                          ("EQ4-CLAMP-LOW", 0.001, 0.1, -2.0), ("EQ4-ZERO-BASELINE", 0.0, 0.6, 1.0)]:
        cases.append({"id": cid, "equation": "EQ-4", "function": "compute_pi_i_eff",
                      "inputs": {"pi_i_baseline": pb, "beta_sm": b, "M_hat": m},
                      "expected": f(ref_pi_i_eff(pb, b, m))})
    for cid, sp, si, tau in [("EQ5-FROM-ZERO", 0.0, 1.0, 5.0), ("EQ5-DECAY", 2.0, 0.0, 5.0),
                             ("EQ5-FAST", 0.0, 1.0, 0.01), ("EQ5-SLOW", 0.5, 1.5, 200.0)]:
        cases.append({"id": cid, "equation": "EQ-5", "function": "accumulate_S_t",
                      "inputs": {"S_prev": sp, "S_input": si, "tau_S": tau},
                      "expected": f(ref_accumulate(d(sp), d(si), tau))})
    for cid, th, g, gn in [("EQ7-NONE", 0.6, 0.0, 0.3), ("EQ7-MID", 0.6, 1.0, 0.3),
                           ("EQ7-LIMIT", 0.6, 1.0, 0.5)]:
        cases.append({"id": cid, "equation": "EQ-7", "function": "apply_ne_threshold_gain",
                      "inputs": {"theta_t": th, "g_NE": g, "gamma_NE": gn},
                      "expected": f(d(th) * (ONE + d(gn) * d(g)))})
    for cid, c, i, ne in [("EQ8-REST", 0.0, 0.0, 0.0), ("EQ8-COST", 1.0, 0.5, 0.0),
                          ("EQ8-NE", 1.0, 0.5, 1.0)]:
        p = DEFAULTS
        val = d(p["theta_0"]) + (d(p["kappa_meta"]) * d(c) - d(p["delta_info"]) * d(i)
                                  + d(p["eta_NE"]) * d(ne)) / d(p["lambda_theta"])
        cases.append({"id": cid, "equation": "EQ-8", "function": "theta_equilibrium",
                      "inputs": {"C": c, "I_val": i, "NE": ne}, "expected": f(val)})
    for cid, bits in [("EQ10-ONE-BIT", 1.0), ("EQ10-TWENTY-BITS", 20.0)]:
        val = d(bits) * d(DEFAULTS["k_B"]) * d(DEFAULTS["T_body"]) * D(2).ln()
        cases.append({"id": cid, "equation": "EQ-10", "function": "landauer_minimum_energy",
                      "inputs": {"n_bits": bits}, "expected": f(val), "unit": "J"})
    return {"fixture": "core-equations", "cases": cases}


def threshold_dynamics(draws: list[float]) -> dict:
    p = dict(DEFAULTS)
    trajectories = []

    def simulate(tid: str, kind: str, n: int, gen: random.Random, theta0: float, zscale: float,
                 use_draws: bool, offset: int) -> dict:
        inputs, S, th = [], d(0.0), d(theta0)
        out = {"S_t": [], "theta_t": [], "ignition_prob": [], "ignition": [], "S_next": []}
        for k in range(n):
            row = {"pi_e": gen.uniform(0.8, 1.5), "z_e": zscale * gen.uniform(0.2, 1.0),
                   "pi_i_baseline": gen.uniform(0.5, 1.5), "z_i": zscale * gen.uniform(0.1, 0.8),
                   "M_hat": gen.uniform(0.0, 0.5), "C_t": gen.uniform(0.5, 2.0),
                   "I_t": gen.uniform(0.1, 1.0), "NE_t": 0.0,
                   "u": draws[offset + k] if use_draws else 1.0}
            inputs.append(row)
            pie = ref_pi_i_eff(row["pi_i_baseline"], p["beta_sm"], row["M_hat"])
            s_in = ref_S_input(row["pi_e"], row["z_e"], pie, row["z_i"])
            S = ref_accumulate(S, s_in, p["tau_S"])
            prob = ref_prob(S, th, p["gamma_sig"])
            fired = d(row["u"]) < prob
            out["S_t"].append(f(S))
            out["theta_t"].append(f(th))
            out["ignition_prob"].append(f(prob))
            out["ignition"].append(bool(fired))
            th = ref_step_theta(th, row["C_t"], row["I_t"], row["NE_t"], fired, p)
            S = d(p["rho_retain"]) * S if fired else S
            out["S_next"].append(f(S))
        return {"id": tid, "kind": kind, "parameters": {k: p[k] for k in (
            "theta_0", "lambda_theta", "kappa_meta", "delta_info", "eta_NE", "gamma_sig",
            "tau_S", "beta_sm", "delta_reset", "rho_retain")},
            "initial": {"S_prev": 0.0, "theta_t": theta0}, "dt": 1.0,
            "noise": {"source": "fixtures/noise-draws.json", "offset": offset} if use_draws
            else {"source": "none (u=1.0: never ignites)"},
            "inputs": inputs, "expected": out}

    trajectories.append(simulate("TD-SUBTHRESHOLD-01", "subthreshold", 40, random.Random(11), 1.5, 0.2, False, 0))
    trajectories.append(simulate("TD-NEAR-THRESHOLD-01", "near_threshold", 40, random.Random(12), 0.9, 1.0, True, 0))
    trajectories.append(simulate("TD-RESET-01", "ignition_and_reset", 40, random.Random(13), 0.5, 1.5, True, 40))
    trajectories.append(simulate("TD-DETERMINISTIC-NOISE-01", "stored_noise", 100, random.Random(14), 0.8, 1.0, True, 80))

    # Half-step sensitivity (S1-FIX-06.5): linear relaxation, no ignition.
    th0, lam, C, I_val = 1.2, p["lambda_theta"], 0.5, 0.2
    theta_star = d(p["theta_0"]) + (d(p["kappa_meta"]) * d(C) - d(p["delta_info"]) * d(I_val)) / d(lam)
    horizon = 10

    def euler(dt: float) -> list[float]:
        th, out = d(th0), [th0]
        for _ in range(int(round(horizon / dt))):
            th = ref_step_theta(th, C, I_val, 0.0, False, p, dt=dt)
            out.append(f(th))
        return out

    exact = [f(theta_star + (d(th0) - theta_star) * (-(d(lam) * d(t))).exp()) for t in range(horizon + 1)]
    full, half = euler(1.0), euler(0.5)
    err_full = abs(d(full[-1]) - d(exact[-1]))
    err_half = abs(d(half[-1]) - d(exact[-1]))
    half_step = {
        "id": "TD-HALF-STEP-01", "kind": "integration_step_sensitivity",
        "parameters": {k: p[k] for k in ("theta_0", "lambda_theta", "kappa_meta", "delta_info")},
        "inputs": {"theta_initial": th0, "C_t": C, "I_t": I_val, "NE_t": 0.0, "horizon": horizon},
        "expected": {"dt_1.0": full, "dt_0.5": half, "exact_at_integer_t": exact,
                     "error_ratio_half_over_full": f(err_half / err_full)},
        "acceptance": {"error_ratio_range": [0.4, 0.6],
                       "note": "Forward Euler is first order: halving dt roughly halves the global error."},
    }
    return {"fixture": "threshold-dynamics", "trajectories": trajectories, "half_step": half_step}


def ulp_steps(x: float, n: int) -> float:
    for _ in range(abs(n)):
        x = math.nextafter(x, math.inf if n > 0 else -math.inf)
    return x


def ignition_boundary() -> dict:
    cases = []
    for theta in (0.6, 0.25, 0.85, 1.0, 1e-3, 123.456):
        for k in (0, 1, -1, 2, -2, 4, -4, 5, -5):
            S = ulp_steps(theta, k)
            cases.append({"id": f"IB-{theta}-{k:+d}ulp", "S_t": S, "theta_t": theta, "ulp_offset": k,
                          "in_band": abs(k) <= TOLERANCE["boundary_band_ulp"],
                          "expected_strict": bool(d(S) > d(theta))})
    return {"fixture": "ignition-boundary",
            "rule": "B = 1 iff S_t > theta_t (EQ-2D, APGI-SCI-001 draft)",
            "band_policy": "Outside the 4-ulp band the strict classification must match exactly; "
                           "inside it the result is recorded and either classification passes "
                           "(§6.1). Bit-identical S_t == theta_t never ignites under the strict rule.",
            "known_conflict": "apgi.core.ignition_criterion(rng=None) uses P >= 0.5 and ignites at "
                              "equality — tracked as DEV-0001.",
            "cases": cases}


def invalid_configurations() -> dict:
    nan, inf = float("nan"), float("inf")
    cases = [
        ("INV-S-NEG-PI-E", "compute_S_t", {"pi_e": -0.1, "z_e": 1.0, "pi_i_eff": 1.0, "z_i": 1.0}),
        ("INV-S-NEG-PI-I", "compute_S_t", {"pi_e": 1.0, "z_e": 1.0, "pi_i_eff": -1.0, "z_i": 1.0}),
        ("INV-S-NAN-Z", "compute_S_t", {"pi_e": 1.0, "z_e": nan, "pi_i_eff": 1.0, "z_i": 1.0}),
        ("INV-S-INF-Z", "compute_S_t", {"pi_e": 1.0, "z_e": 1.0, "pi_i_eff": 1.0, "z_i": inf}),
        ("INV-PIEFF-NEG", "compute_pi_i_eff", {"pi_i_baseline": -1.0, "beta_sm": 0.6, "M_hat": 0.0}),
        ("INV-PIEFF-NAN", "compute_pi_i_eff", {"pi_i_baseline": 1.0, "beta_sm": nan, "M_hat": 0.0}),
        ("INV-ACC-TAU-ZERO", "accumulate_S_t", {"S_prev": 0.0, "S_input": 1.0, "tau_S": 0.0}),
        ("INV-ACC-TAU-NEG", "accumulate_S_t", {"S_prev": 0.0, "S_input": 1.0, "tau_S": -5.0}),
        ("INV-ACC-DT-ZERO", "accumulate_S_t", {"S_prev": 0.0, "S_input": 1.0, "tau_S": 5.0, "dt": 0.0}),
        ("INV-ACC-NAN", "accumulate_S_t", {"S_prev": nan, "S_input": 1.0, "tau_S": 5.0}),
        ("INV-P-GAMMA-ZERO", "ignition_probability", {"S_t": 1.0, "theta_t": 0.5, "gamma_sig": 0.0}),
        ("INV-P-GAMMA-NEG", "ignition_probability", {"S_t": 1.0, "theta_t": 0.5, "gamma_sig": -5.0}),
        ("INV-P-NAN-S", "ignition_probability", {"S_t": nan, "theta_t": 0.5}),
        ("INV-P-INF-THETA", "ignition_probability", {"S_t": 1.0, "theta_t": -inf}),
        ("INV-THETA-NEG-LAMBDA", "step_theta", {"theta_t": 0.6, "C_t": 0.0, "I_t": 0.0, "lambda_theta": -0.1}),
        ("INV-THETA-NEG-RESET", "step_theta", {"theta_t": 0.6, "C_t": 0.0, "I_t": 0.0, "delta_reset": -0.2}),
        ("INV-THETA-DT-ZERO", "step_theta", {"theta_t": 0.6, "C_t": 0.0, "I_t": 0.0, "dt": 0.0}),
        ("INV-THETA-NAN-C", "step_theta", {"theta_t": 0.6, "C_t": nan, "I_t": 0.0}),
        ("INV-RESET-RHO-HIGH", "post_ignition_reset", {"S_t": 1.0, "fired": True, "rho_retain": 1.5}),
        ("INV-RESET-RHO-NEG", "post_ignition_reset", {"S_t": 1.0, "fired": True, "rho_retain": -0.1}),
        ("INV-NE-NEG-GAIN", "apply_ne_threshold_gain", {"theta_t": 0.6, "g_NE": -1.0}),
        ("INV-NE-SUBDOMINANCE", "apply_ne_threshold_gain", {"theta_t": 0.6, "g_NE": 2.0, "gamma_NE": 0.3}),
        ("INV-EQ-LAMBDA-ZERO", "theta_equilibrium", {"C": 1.0, "I_val": 0.5, "lambda_theta": 0.0}),
        ("INV-STRICT-NAN", "ignition_decision_strict", {"S_t": nan, "theta_t": 0.5}),
    ]
    valid_clamping = [
        {"id": "CLAMP-PIEFF-HIGH", "function": "compute_pi_i_eff",
         "inputs": {"pi_i_baseline": 5.0, "beta_sm": 1.2, "M_hat": 2.0}, "expected": DEFAULTS["PI_MAX"],
         "note": "Valid clamping (Math Spec §4.2): does not raise."},
        {"id": "CLAMP-PIEFF-LOW", "function": "compute_pi_i_eff",
         "inputs": {"pi_i_baseline": 0.001, "beta_sm": 0.1, "M_hat": -2.0}, "expected": DEFAULTS["PI_MIN"],
         "note": "Valid clamping: does not raise."},
    ]
    return {"fixture": "invalid-configurations",
            "policy": "Invalid configurations raise ValueError; valid clamping never raises; no silent clipping of invalid domains.",
            "must_raise": [{"id": cid, "function": fn, "inputs": {k: enc(v) for k, v in inp.items()},
                            "expected": {"raises": "ValueError"}} for cid, fn, inp in cases],
            "valid_clamping": valid_clamping}


def noise_draws() -> tuple[dict, list[float]]:
    gen = random.Random(NOISE_SEED)
    draws = [gen.random() for _ in range(4000)]
    return ({"fixture": "noise-draws", "distribution": "uniform[0,1)", "count": len(draws),
             "provenance": f"Python random.Random({NOISE_SEED}) Mersenne Twister; stored as data so that "
                           "consumers in any language read identical draws (S1-FIX-09).",
             "consumption_rule": "ignition iff draw < P(ign); one draw per trial in order from `offset`",
             "draws": draws}, draws)


def golden_vectors(draws: list[float]) -> dict:
    vectors: list[dict] = []
    rng = random.Random(4242)
    for i in range(200):  # ordinary
        vectors.append(vector("ordinary", i, settle_draw(base_params(rng), rng)))
    for i in range(200):  # near-threshold: θ_t placed within ±1e-3 of S_t
        v = base_params(rng)
        pie = ref_pi_i_eff(v["pi_i_baseline"], v["beta_sm"], v["M_hat"])
        s_t = ref_accumulate(d(v["S_prev"]), ref_S_input(v["pi_e"], v["z_e"], pie, v["z_i"]), v["tau_S"])
        v["theta_t"] = f(s_t) + rng.uniform(-1e-3, 1e-3)
        vectors.append(vector("near_threshold", i, settle_draw(v, rng)))
    edge_specs = []
    for i in range(150):  # zero / negative / extreme / invalid
        v = base_params(rng)
        kind = i % 6
        if kind == 0:
            v.update(z_e=0.0, z_i=0.0, S_prev=0.0)
        elif kind == 1:
            v.update(z_e=-abs(v["z_e"]), z_i=-abs(v["z_i"]))
        elif kind == 2:
            v.update(z_e=rng.choice([1e6, -1e6]), pi_e=rng.uniform(5, 10))
        elif kind == 3:
            v.update(pi_e=0.0, pi_i_baseline=0.0)
        elif kind == 4:
            v.update(theta_t=rng.uniform(-50, -1), z_e=rng.uniform(-1e-12, 1e-12))
        if kind == 5:
            field, value, reason = [("pi_e", -1.0, "negative precision"), ("z_i", float("nan"), "NaN input"),
                                    ("tau_S", 0.0, "non-positive timescale"), ("gamma_sig", -2.0, "negative steepness"),
                                    ("rho_retain", 1.5, "retention outside [0,1]"),
                                    ("lambda_theta", -0.2, "negative rate"),
                                    ("C_t", float("inf"), "infinite input")][i // 6 % 7]
            edge_specs.append(invalid_vector(i, v, field, value, reason))
        else:
            edge_specs.append(vector("edge", i, settle_draw(v, rng)))
    vectors.extend(edge_specs)
    for i in range(150):  # precision variations across orders of magnitude and clamp regimes
        v = base_params(rng)
        v["pi_e"] = 10 ** rng.uniform(-3, 1)
        v["pi_i_baseline"] = 10 ** rng.uniform(-3, 1.5)
        v["beta_sm"] = rng.uniform(0.0, 1.2)
        v["M_hat"] = rng.uniform(-2.0, 2.0)
        vectors.append(vector("precision", i, settle_draw(v, rng)))
    for i in range(150):  # threshold / refractory variations (forced fire / no-fire)
        v = base_params(rng)
        v["delta_reset"] = rng.uniform(0.0, 1.0)
        v["rho_retain"] = rng.uniform(0.0, 1.0)
        v["lambda_theta"] = rng.uniform(0.0, 1.0)
        v["u"] = 0.0 if i % 2 == 0 else 0.999999999999
        if ref_trial(v)["_margin"] < 1e-9:
            v["u"] = 0.5
        vectors.append(vector("threshold_refractory", i, settle_draw(v, rng)))
    trajectories = []
    for i in range(150):  # seeded / dynamic: 20-step trajectories from stored draws
        gen = random.Random(10_000 + i)
        p = {k: base_params(gen)[k] for k in ("theta_0", "lambda_theta", "kappa_meta", "delta_info",
                                              "eta_NE", "gamma_sig", "tau_S", "beta_sm",
                                              "delta_reset", "rho_retain")}
        offset = (i * 20) % (len(draws) - 20)
        S, th = d(0.0), d(gen.uniform(0.3, 1.2))
        theta_init = f(th)
        rows, out = [], {"S_t": [], "theta_next": [], "ignition": [], "S_next": []}
        ambiguous = False
        for k in range(20):
            row = {"pi_e": gen.uniform(0.5, 2.0), "z_e": gen.uniform(-2, 2),
                   "pi_i_baseline": gen.uniform(0.5, 2.0), "z_i": gen.uniform(-2, 2),
                   "M_hat": gen.uniform(-1, 1), "C_t": gen.uniform(0, 2), "I_t": gen.uniform(0, 1),
                   "NE_t": gen.uniform(0, 1)}
            rows.append(row)
            pie = ref_pi_i_eff(row["pi_i_baseline"], p["beta_sm"], row["M_hat"])
            S = ref_accumulate(S, ref_S_input(row["pi_e"], row["z_e"], pie, row["z_i"]), p["tau_S"])
            prob = ref_prob(S, th, p["gamma_sig"])
            u = d(draws[offset + k])
            ambiguous |= abs(u - prob) < D("1e-9")
            fired = u < prob
            th = ref_step_theta(th, row["C_t"], row["I_t"], row["NE_t"], fired, p)
            out["S_t"].append(f(S))
            S = d(p["rho_retain"]) * S if fired else S
            out["theta_next"].append(f(th))
            out["ignition"].append(bool(fired))
            out["S_next"].append(f(S))
        trajectories.append({"id": f"GV-DYN-{i:04d}", "category": "seeded_dynamic", "parameters": p,
                             "initial": {"S_prev": 0.0, "theta_t": theta_init},
                             "noise": {"source": "fixtures/noise-draws.json", "offset": offset},
                             "decision_margin_below_1e-9": ambiguous,
                             "inputs": rows, "expected": out})
    counts: dict[str, int] = {}
    for v in vectors:
        counts[v["category"]] = counts.get(v["category"], 0) + 1
    counts["seeded_dynamic"] = len(trajectories)
    return {"fixture": "golden-vectors", "counts": counts, "total": len(vectors) + len(trajectories),
            "single_step_function": "apgi.core.run_trial with a stored-draw generator (u)",
            "vectors": vectors, "trajectories": trajectories}


def wrap(payload: dict) -> dict:
    return {"schema": "fixtures/fixture.schema.json", "generator": "fixtures/generate_fixtures.py",
            "generator_version": GENERATOR_VERSION, "model_variant": MODEL_VARIANT,
            "model_version": MODEL_VERSION, "reference_arithmetic": "decimal, 60 significant digits",
            "tolerance": TOLERANCE, "approval": APPROVAL, **payload}


def build() -> dict[str, str]:
    noise, draws = noise_draws()
    files = {
        "core-equations.json": wrap(core_equations()),
        "threshold-dynamics.json": wrap(threshold_dynamics(draws)),
        "ignition-boundary.json": wrap(ignition_boundary()),
        "invalid-configurations.json": wrap(invalid_configurations()),
        "noise-draws.json": wrap(noise),
        "golden-vectors.json": wrap(golden_vectors(draws)),
    }
    rendered = {name: json.dumps(body, indent=1, ensure_ascii=False) + "\n" for name, body in files.items()}
    index = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in sorted(rendered.items())}
    rendered["INDEX.json"] = json.dumps({"generator_version": GENERATOR_VERSION, "files": index},
                                        indent=1) + "\n"
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="fail if any fixture would change")
    args = parser.parse_args(argv)
    rendered = build()
    drift = []
    for name, text in rendered.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                drift.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if drift:
        print("fixture drift: " + ", ".join(drift), file=sys.stderr)
        return 1
    print(("checked " if args.check else "wrote ") + ", ".join(sorted(rendered)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
