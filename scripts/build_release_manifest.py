"""Build and validate the release manifest for the current commit (S1-FWK-10, IMP-001).

    python scripts/build_release_manifest.py --out release-manifest.json [--dist dist/]

The manifest pins the protocol lock, the specification bundle, the fixture
index, every schema and (with --dist) the built wheel/sdist digests, then is
validated against releases/release-manifest.schema.json; the script exits 1
on any verification or schema failure. Certification status is always
"Not certified" here: only the release authority can change it.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import subprocess
import sys
import tomllib

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from apgi.protocols import verify_lock  # noqa: E402
from apgi.spec_bundle import verify_bundle  # noqa: E402

SCHEMAS = ["protocols/schemas/protocol.schema.json", "fixtures/fixture.schema.json",
           "gates/gate-table.schema.json", "releases/release-manifest.schema.json"]


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(dist: pathlib.Path | None) -> dict:
    lock = verify_lock(ROOT / "protocols")
    bundle = verify_bundle(ROOT)
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                            check=True).stdout.strip()
    index = json.loads((ROOT / "fixtures/INDEX.json").read_text(encoding="utf-8"))
    approval = json.loads((ROOT / "fixtures/core-equations.json").read_text(encoding="utf-8"))["approval"]
    artifacts = []
    if dist is not None:
        artifacts = [{"path": p.name, "sha256": sha(p)} for p in sorted(dist.iterdir()) if p.is_file()]
    return {
        "manifest_format": 1,
        "component": "apgi-framework",
        "version": project["version"],
        "source_commit": commit,
        "created_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "protocol_lock": {"release": lock["release"], "manifest_sha256": lock["manifest_sha256"],
                          "anchor": lock["anchor"]},
        "spec_bundle": {"sha256sums_sha256": bundle["sha256sums_sha256"], "file_count": bundle["file_count"]},
        "fixtures": {"generator_version": index["generator_version"], "index_sha256": sha(ROOT / "fixtures/INDEX.json"),
                     "approval_status": approval["status"]},
        "schemas": {rel: sha(ROOT / rel) for rel in SCHEMAS},
        "artifacts": artifacts,
        "dependencies": {"declared": project["dependencies"],
                         "lockfile_sha256": sha(ROOT / "environment.lock.yml")},
        "model_variant": {"id": "MV-CORE-DISCRETE-1", "model_version": "1.0.0"},
        "compatibility_matrix": "releases/compatibility-matrix.yaml",
        "certification": {"status": "Not certified", "independence_level": "Self-attested", "approvers": []},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--dist", type=pathlib.Path)
    args = parser.parse_args(argv)
    manifest = build(args.dist)
    schema = json.loads((ROOT / "releases/release-manifest.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(manifest, schema, format_checker=jsonschema.FormatChecker())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"release manifest valid: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
