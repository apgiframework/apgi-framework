"""REP-002: record the numerical environment and a same-seed repeat-run digest.

Captures Python/NumPy/SciPy versions, platform and machine, BLAS/LAPACK
build information, thread-count environment variables, and the FMA/SIMD
features NumPy reports. It then runs the stored-draw golden trajectories and
a seeded APGICoreIntegration session twice, hashing the float64 outputs, so
two machines (e.g. Linux x86-64 and macOS ARM64 in CI) can compare:

* same machine, same seed  -> digests must be bitwise identical;
* across platforms         -> compare values within the §6.1 tolerance
                              (run the fixture tests; digests may differ).

    python scripts/record_environment.py --out evidence/env/<platform>.json
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import pathlib
import platform
import sys

import numpy as np
import scipy

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from apgi import core  # noqa: E402
from apgi.datasets import make_sample_session  # noqa: E402
from apgi.integration import APGICoreIntegration  # noqa: E402

THREAD_VARS = ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"]


def blas_info() -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            np.show_config()
        except Exception as exc:  # pragma: no cover - diagnostic only
            print(f"show_config failed: {exc}")
    return buf.getvalue()


def simd_features() -> dict:
    try:
        from numpy._core._multiarray_umath import __cpu_features__ as feats  # numpy >= 2
    except ImportError:  # pragma: no cover
        try:
            from numpy.core._multiarray_umath import __cpu_features__ as feats
        except ImportError:
            return {}
    return {k: bool(v) for k, v in sorted(feats.items()) if k in {"FMA3", "AVX2", "AVX512F", "NEON", "ASIMD", "ASIMDHP", "SSE42"}}


def run_digest(seed: int) -> str:
    session = make_sample_session(n_trials=500, seed=seed)
    integ = APGICoreIntegration()
    rng = np.random.default_rng(seed)
    records = integ.run_sequence(session["pi_e"], session["z_e"], session["pi_i"], session["z_i"],
                                 C_t=session["C_metabolic"], I_t=session["V_information"], rng=rng)
    values = np.array([[r.S_t, r.theta_t, float(r.ignition)] for r in records], dtype=np.float64)
    draws = json.loads((ROOT / "fixtures/noise-draws.json").read_text())["draws"][:200]
    theta, S, traj = 0.8, 0.0, []
    for u in draws:
        class _Draw:
            def random(self, _u=u):
                return _u
        out = core.run_trial(1.1, 0.7, 1.0, 0.4, 0.2, 1.0, 0.5, theta, S_prev=S, rng=_Draw())
        S, theta = out["S_next"], out["theta_next"]
        traj.append((out["S_t"], out["theta_next"]))
    digest = hashlib.sha256(values.tobytes())
    digest.update(np.array(traj, dtype=np.float64).tobytes())
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args(argv)
    first, second = run_digest(args.seed), run_digest(args.seed)
    record = {
        "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
        "platform": platform.platform(), "machine": platform.machine(), "system": platform.system(),
        "thread_env": {k: os.environ.get(k) for k in THREAD_VARS},
        "cpu_features": simd_features(),
        "blas_lapack": blas_info(),
        "seed": args.seed,
        "repeat_run_digests": [first, second],
        "bitwise_repeatable": first == second,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"{record['system']} {record['machine']}: repeatable={record['bitwise_repeatable']} digest={first[:16]}")
    return 0 if record["bitwise_repeatable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
