#!/usr/bin/env python3
"""Refresh provenance.source_files in the eight APGI protocol JSONs.

Usage:
    python3 update_provenance.py <protocols_dir> <FINAL_dir> [--dry-run]

For each protocol_*.json it replaces the four source entries with the
current FINAL file names and their SHA-256. Nothing else in the JSON changes
(key order, 2-space indent, UTF-8 and the trailing newline are preserved).
"""
import hashlib, json, pathlib, sys

SOURCES = [  # old name in JSON -> current file in FINAL
    ("OSF-Preregistration.docx",        "APGI-OSF-Preregistration.docx"),
    ("Protocols.docx",                  "APGI-Protocols.docx"),
    ("Mathematical-Specification.docx", "APGI-Mathematical-Specifications.docx"),
    ("Notation-Appendix.docx",          "APGI-Notation-Appendix.docx"),
]

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    pdir, fdir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    dry = "--dry-run" in sys.argv
    new = []
    for _, name in SOURCES:
        path = fdir / name
        if not path.is_file():
            sys.exit(f"Missing source document: {path}")
        new.append({"file": name, "sha256": sha256(path)})
        print(f"{name:40s} {new[-1]['sha256']}")
    files = sorted(pdir.glob("protocol_*.json"))
    if len(files) != 8:
        sys.exit(f"Expected 8 protocol files in {pdir}, found {len(files)}")
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        old = d["provenance"]["source_files"]
        d["provenance"]["source_files"] = new
        changed = old != new
        print(f"{f.name:40s} {'updated' if changed else 'already current'}")
        if changed and not dry:
            f.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Dry run: no files written." if dry else "Done.")

if __name__ == "__main__":
    main()
