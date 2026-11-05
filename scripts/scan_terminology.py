"""SCI-006 terminology scan: APGI expands only to "Allostatic Precision-Gated Ignition".

Scans every tracked text file (git ls-files) — source, docs, notebooks,
metadata (CITATION.cff, .zenodo.json, pyproject.toml), figure captions and
SVG text — for the forbidden expansions named in APGI-VAL-SPEC-1.2 and for
any "APGI (...)" or "... (APGI)" expansion that is not the canonical one.
Binary formats (PDF/PNG) are not decoded; their SVG/caption sources are.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANONICAL = "Allostatic Precision-Gated Ignition"
FORBIDDEN = ["Adaptive Predictive Global Integration", "Active Phase-Transition Global Ignition"]
TEXT_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml", ".cff", ".toml", ".txt", ".ipynb",
                 ".svg", ".html", ".js", ".sh", ".cfg", ".tex", ".csv"}
# "<Four Capitalised Words> (APGI)" or "APGI (<expansion>)"
EXPANSION_BEFORE = re.compile(r"((?:[A-Z][\w-]*[\s-]+){2,5}[A-Z][\w-]*)\s*\(APGI\)")
EXPANSION_AFTER = re.compile(r"APGI\s*\(((?:[A-Z][\w-]*[\s-]+){2,5}[A-Z][\w-]*)\)")
SELF = {"scripts/scan_terminology.py", "tests/test_validation_tooling.py"}


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [line for line in out.stdout.splitlines() if pathlib.Path(line).suffix in TEXT_SUFFIXES]


def scan(files: list[str] | None = None) -> dict:
    findings = []
    files = files if files is not None else tracked_files()
    for rel in files:
        if rel in SELF:
            continue
        path = ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        norm = re.sub(r"\s+", " ", text)
        for bad in FORBIDDEN:
            if bad.lower() in norm.lower():
                findings.append({"file": rel, "finding": f"forbidden expansion: {bad}"})
        for pattern in (EXPANSION_BEFORE, EXPANSION_AFTER):
            for match in pattern.finditer(norm):
                expansion = re.sub(r"[\s]+", " ", match.group(1)).strip()
                if not expansion.endswith(CANONICAL) and expansion != CANONICAL:
                    findings.append({"file": rel, "finding": f"non-canonical expansion: {expansion}"})
    return {"canonical": CANONICAL, "files_scanned": len(files), "findings": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--report", type=pathlib.Path)
    args = parser.parse_args(argv)
    result = scan()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for f in result["findings"]:
        print(f"FINDING {f}", file=sys.stderr)
    print(f"terminology scan: {result['files_scanned']} files, {len(result['findings'])} findings")
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
