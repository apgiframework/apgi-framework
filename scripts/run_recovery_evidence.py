"""AUD-EXEC-01: run the 30-simulation x 300-trial recovery case and retain evidence.

Writes evidence/runs/AUD-EXEC-01-recovery.json with the measured recovery
correlations, the declared targets, the seed, and the software environment.
The targets are the thresholds asserted in
tests/test_parameter_recovery.py::TestRunRecoverySimulation::test_recovery_criteria
("Table 13 targets, relaxed slightly for finite-sample tolerance"); they are
not approved acceptance criteria.
"""

from __future__ import annotations

import datetime as _dt
import json
import pathlib
import platform
import subprocess
import sys

import numpy as np
import scipy

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from apgi.parameter_recovery import run_recovery_simulation  # noqa: E402

TARGETS = {"r_theta_0": 0.70, "r_tau_S": 0.65, "r_pi_i": 0.60, "r_beta_sm": 0.40, "r_gamma_sig": 0.40}
CONFIG = {"n_simulations": 30, "n_trials_per_sim": 300, "seed": 2024}


def main() -> int:
    started = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    results = run_recovery_simulation(**CONFIG)
    finished = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    measured = {k: float(results[k]) for k in TARGETS}
    outcome = {k: measured[k] > TARGETS[k] for k in TARGETS}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True, check=False).stdout.strip()
    record = {
        "task": "AUD-EXEC-01",
        "config": CONFIG,
        "targets_strictly_greater_than": TARGETS,
        "measured": measured,
        "passed": outcome,
        "all_passed": all(outcome.values()),
        "started_utc": started,
        "finished_utc": finished,
        "source_commit": commit,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "platform": platform.platform()},
        "note": "Targets are test thresholds, not approved acceptance criteria.",
    }
    out = ROOT / "evidence" / "runs" / "AUD-EXEC-01-recovery.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    return 0 if record["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
