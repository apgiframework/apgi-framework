"""SCI-004 notation scan: every public scientific identifier maps to the notation map.

Scans public function/method arguments and module-level UPPER_CASE constants
in the scientific modules, checks each against
specifications/notation/symbol-map.yaml, checks every mapped registry ID
exists in specifications/model/parameter-registry.yaml, and flags bare
Greek-family identifiers that are not explicitly recorded as legacy.

Exit status 0 = zero findings. Writes the findings report with --report PATH.
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODULES = ["core", "precision", "integration", "clinical", "normalizer", "parameter_recovery",
           "quantities", "hierarchy_levels", "extensions/epistemic", "extensions/hierarchical",
           "extensions/liquid_network"]
GREEK_FAMILIES = {"alpha", "beta", "gamma", "delta", "eta", "kappa", "lambda", "rho", "tau",
                  "theta", "pi", "mu", "sigma", "epsilon"}
IGNORED = {"self", "cls", "value", "other", "mod", "name", "seconds", "level_id_", "variant_id",
           "model_version", "params", "step_seconds", "allow_alternative", "z", "fields", "op"}


def identifiers(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_") or node.name == "__init__"):
            for arg in node.args.args + node.args.kwonlyargs:
                names.add(arg.arg)
    for node in tree.body:
        targets = [node.target] if isinstance(node, ast.AnnAssign) else getattr(node, "targets", [])
        for target in targets:
            if isinstance(target, ast.Name) and target.id.isupper() and not target.id.startswith("_"):
                names.add(target.id)
    return names - IGNORED


def scan() -> dict:
    symbol_map = yaml.safe_load((ROOT / "specifications/notation/symbol-map.yaml").read_text(encoding="utf-8"))
    registry = yaml.safe_load((ROOT / "specifications/model/parameter-registry.yaml").read_text(encoding="utf-8"))
    registry_ids = {e["id"] for e in registry["entries"]}
    symbols, non_symbols = symbol_map["symbols"], set(symbol_map["non_symbols"])
    findings, seen = [], {}
    for module in MODULES:
        path = ROOT / "src" / "apgi" / f"{module}.py"
        for name in sorted(identifiers(path)):
            seen.setdefault(name, []).append(module)
    for name, modules in sorted(seen.items()):
        if name in non_symbols:
            continue
        entry = symbols.get(name)
        if entry is None:
            findings.append({"identifier": name, "modules": modules, "finding": "unmapped identifier"})
            continue
        if entry["registry"] not in registry_ids:
            findings.append({"identifier": name, "finding": f"unknown registry id {entry['registry']}"})
        if name.lower() in GREEK_FAMILIES and not entry.get("legacy_bare"):
            findings.append({"identifier": name, "finding": "bare Greek-family identifier without disambiguation"})
    legacy = sorted(n for n, e in symbols.items() if e.get("legacy_bare"))
    return {"scanned_modules": MODULES, "identifiers": len(seen), "findings": findings,
            "legacy_bare_identifiers": legacy}


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
    print(f"notation scan: {result['identifiers']} identifiers, {len(result['findings'])} findings, "
          f"legacy bare: {result['legacy_bare_identifiers']}")
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
