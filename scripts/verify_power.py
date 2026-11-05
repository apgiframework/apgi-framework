"""REP-003: independently recompute registered power and sample-size figures with scipy.

Every classical power/sample-size statement in protocols/*.json
``power_analysis`` is recomputed here from first principles (noncentral t,
Fisher z) with scipy — not with any APGI code — and compared with the
registered value per APGI-VAL-SPEC-1.2 §6.1: equal sample size after rounding
up, and power within 1e-6 relative. Registered powers are stated to two
decimals, so each power comparison also reports agreement at the registered
precision; only the 1e-6 comparison counts as a §6.1 match.

Designs without a closed-form classical calculation (simulation, Bayesian,
sequential stopping rules, regression F tests whose numerator df is not
registered) are reported ``not_reproducible`` with the reason — no value is
invented for them.

Outcomes that do not match must be acknowledged in
specifications/governance/deviations.yaml (by ``case`` ID); the script exits
1 if any mismatch or non-reproducible case is unacknowledged.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

import scipy
import yaml
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from apgi.protocols import load_protocols  # noqa: E402

REL_TOL = 1e-6


def power_one_sample_t(d: float, n: int, alpha: float, tails: int = 2) -> float:
    df, nc = n - 1, d * math.sqrt(n)
    if tails == 2:
        crit = stats.t.ppf(1 - alpha / 2, df)
        return float(stats.nct.sf(crit, df, nc) + stats.nct.cdf(-crit, df, nc))
    crit = stats.t.ppf(1 - alpha, df)
    return float(stats.nct.sf(crit, df, nc))


def n_one_sample_t(d: float, alpha: float, power: float, tails: int = 2) -> int:
    n = 2
    while power_one_sample_t(d, n, alpha, tails) < power:
        n += 1
    return n


def n_correlation(r: float, alpha: float, power: float) -> int:
    z = stats.norm.ppf
    return math.ceil(((z(1 - alpha / 2) + z(power)) / math.atanh(r)) ** 2 + 3)


def power_correlation(r: float, n: int, alpha: float) -> float:
    z = stats.norm.ppf
    shift = math.atanh(r) * math.sqrt(n - 3)
    crit = z(1 - alpha / 2)
    return float(stats.norm.sf(crit - shift) + stats.norm.cdf(-crit - shift))


def compare_power(registered: float, reference: float) -> dict:
    decimals = max(0, len(repr(registered).split(".")[-1])) if "." in repr(registered) else 0
    return {"registered": registered, "reference": reference,
            "match_1e-6_relative": abs(reference - registered) <= REL_TOL * abs(reference),
            "match_at_registered_precision": round(reference, decimals) == registered}


def cases(protocols) -> list[dict]:
    out: list[dict] = []
    p0 = protocols["APGI-P00"]["power_analysis"]
    out.append({"case": "PWR-P00-N", "protocol_id": "APGI-P00", "design": "two-tailed Pearson correlation (Fisher z)",
                "inputs": {"r": p0["effect_size_r"], "alpha": p0["alpha"], "power": p0["power"]},
                "n_registered": p0["n_required"],
                "n_reference": n_correlation(p0["effect_size_r"], p0["alpha"], p0["power"])})
    for pid, key, tails in (("APGI-P01", "n_required", 2), ("APGI-P03", "n_required", 2),
                            ("APGI-P04", "n_required", 2), ("APGI-P05", "n_required", 2)):
        pa = protocols[pid]["power_analysis"]
        d, a, pw = pa["effect_size_d"], pa["alpha"], pa["power"]
        n_ref = n_one_sample_t(d, a, pw, tails)
        entry = {"case": f"PWR-{pid[-3:]}-N", "protocol_id": pid,
                 "design": "paired / one-sample t, two-tailed (fixed-n reference)",
                 "inputs": {"d": d, "alpha": a, "power": pw}, "n_registered": pa[key], "n_reference": n_ref,
                 "power_at_reference_n": power_one_sample_t(d, n_ref, a, tails)}
        if pa.get("design_type") == "sequential":
            entry["note"] = "Registered design is sequential; the fixed-n reference checks only the nominal n_required."
        out.append(entry)
        if "power_at_minimum" in pa and pa.get("n_minimum"):
            out.append({"case": f"PWR-{pid[-3:]}-PMIN", "protocol_id": pid,
                        "design": "power at registered minimum n (paired t, two-tailed)",
                        "inputs": {"d": d, "alpha": a, "n": pa["n_minimum"]},
                        "power": compare_power(pa["power_at_minimum"],
                                               power_one_sample_t(d, pa["n_minimum"], a, tails))})
    p3 = protocols["APGI-P03"]["power_analysis"]["secondary_correlation"]
    out.append({"case": "PWR-P03-SECONDARY-R", "protocol_id": "APGI-P03",
                "design": "two-tailed Pearson correlation (Fisher z), alpha 0.05 assumed",
                "inputs": {"r": p3["r"], "n": p3["n"], "alpha": 0.05},
                "power": compare_power(p3["power"], power_correlation(p3["r"], p3["n"], 0.05))})
    p1f = protocols["APGI-P01"]["power_analysis"]["pred_1f"]
    out.append({"case": "PWR-P01-1F", "protocol_id": "APGI-P01",
                "design": "standardized slope treated as correlation (Fisher z)",
                "inputs": {"r": p1f["standardized_slope"], "alpha": p1f["alpha"], "power": p1f["power"]},
                "n_registered_available": p1f["n"],
                "n_reference": n_correlation(p1f["standardized_slope"], p1f["alpha"], p1f["power"]),
                "comparison": "registered n is the available sample; check n_reference <= n_registered_available"})
    p7 = protocols["APGI-P07"]["power_analysis"]
    out.append({"case": "PWR-P07-F", "protocol_id": "APGI-P07", "design": "regression F test (f²)",
                "inputs": {"f2": p7["effect_size_f_squared"], "alpha": p7["alpha"], "n": p7["n_target"]},
                "status": "not_reproducible",
                "reason": "numerator df and covariate count are not registered; the noncentral-F power "
                          "cannot be recomputed without them (registered power_status: approximation)."})
    for pid in ("APGI-P02", "APGI-P06"):
        out.append({"case": f"PWR-{pid[-3:]}", "protocol_id": pid,
                    "design": protocols[pid]["power_analysis"]["design_type"],
                    "status": "not_applicable",
                    "reason": "no classical power calculation registered (simulation/Bayesian design)"})
    for c in out:
        if "status" in c:
            continue
        ok = True
        if "n_registered" in c:
            c["n_match"] = c["n_registered"] == c["n_reference"]
            ok &= c["n_match"]
        if "n_registered_available" in c:
            c["n_match"] = c["n_reference"] <= c["n_registered_available"]
            ok &= c["n_match"]
        if "power" in c:
            ok &= c["power"]["match_1e-6_relative"]
        c["status"] = "match" if ok else "mismatch"
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--report", type=pathlib.Path,
                        default=ROOT / "evidence" / "power" / "power-comparison.json")
    args = parser.parse_args(argv)
    protocols = load_protocols(ROOT / "protocols")
    results = cases(protocols)
    deviations = yaml.safe_load((ROOT / "specifications/governance/deviations.yaml").read_text(encoding="utf-8"))
    acknowledged = {c for d in deviations["entries"] for c in d.get("power_cases", [])}
    unack = [r["case"] for r in results if r["status"] in {"mismatch", "not_reproducible"}
             and r["case"] not in acknowledged]
    report = {"reference_library": f"scipy {scipy.__version__}", "tolerance": {"n": "ceil equality", "power_relative": REL_TOL},
              "cases": results, "unacknowledged": unack}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for r in results:
        print(f"{r['case']:<22} {r['status']}")
    if unack:
        print(f"unacknowledged non-matching cases: {unack}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
