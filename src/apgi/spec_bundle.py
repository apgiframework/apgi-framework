"""Consumer-side verification of the APGI specification bundle (S1-FWK-04).

The bundle is the set of authority files listed in ``bundle/SHA256SUMS``
(protocols, specifications, fixtures, traceability, gates, release schemas).
Consumers call :func:`verify_bundle` before reading any of them; a missing,
altered or unlisted file raises :class:`BundleVerificationError` and nothing
is returned.
"""

from __future__ import annotations

import hashlib
import os
import pathlib

__all__ = ["BUNDLE_DIRS", "BundleVerificationError", "bundle_files", "verify_bundle", "default_root"]

BUNDLE_FORMAT = 1
BUNDLE_DIRS = ("protocols", "specifications", "fixtures", "traceability", "gates", "releases")
_SUFFIXES = {".json", ".yaml", ".yml", ".md", ".py"}


class BundleVerificationError(RuntimeError):
    """The specification bundle failed checksum verification."""

    code = "APGI-BUNDLE-CHECKSUM"


def default_root() -> pathlib.Path:
    env = os.environ.get("APGI_SPEC_ROOT")
    return pathlib.Path(env) if env else pathlib.Path(__file__).resolve().parents[2]


def bundle_files(root: pathlib.Path) -> list[str]:
    """Every file that belongs to the bundle, as sorted POSIX relative paths."""
    files = []
    for top in BUNDLE_DIRS:
        base = root / top
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in _SUFFIXES and "__pycache__" not in path.parts:
                files.append(path.relative_to(root).as_posix())
    return sorted(files)


def _parse_sums(text: str) -> dict[str, str]:
    sums: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, _, rel = line.partition("  ")
        if len(digest) != 64 or not rel:
            raise BundleVerificationError(f"malformed SHA256SUMS line: {line!r}")
        if rel in sums:
            raise BundleVerificationError(f"duplicate SHA256SUMS entry: {rel}")
        sums[rel] = digest
    return sums


def verify_bundle(root: str | os.PathLike[str] | None = None) -> dict:
    """Verify every bundle file against ``bundle/SHA256SUMS``.

    Returns a record with the digest of SHA256SUMS and the file count.

    Raises:
        BundleVerificationError: missing SHA256SUMS, missing/altered file, or
            a bundle-directory file that is not listed.
    """
    base = pathlib.Path(root) if root is not None else default_root()
    sums_path = base / "bundle" / "SHA256SUMS"
    if not sums_path.is_file():
        raise BundleVerificationError(f"bundle checksum file not found: {sums_path}")
    raw = sums_path.read_bytes()
    sums = _parse_sums(raw.decode("utf-8"))
    problems = []
    for rel, expected in sums.items():
        path = (base / rel).resolve()
        if base.resolve() not in path.parents:
            problems.append(f"path escapes bundle root: {rel}")
            continue
        if not path.is_file():
            problems.append(f"missing: {rel}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            problems.append(f"checksum mismatch: {rel}")
    for rel in bundle_files(base):
        if rel not in sums:
            problems.append(f"unlisted: {rel}")
    if problems:
        raise BundleVerificationError("specification bundle verification failed: " + "; ".join(problems[:20]))
    return {"bundle_format": BUNDLE_FORMAT, "sha256sums_sha256": hashlib.sha256(raw).hexdigest(),
            "file_count": len(sums)}
