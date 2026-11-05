"""Lock-verified, all-or-nothing loader for the registered protocol definitions.

APGI-VAL-SPEC-1.2 requirements implemented here:

* **REP-001** — every definition file is verified against the SHA-256 lock
  manifest (``protocols/MANIFEST.json``) *before* any file is parsed. A
  missing, extra, or altered file aborts the whole load; nothing is returned
  and callers therefore cannot produce output from altered definitions.
* **PRO-002** — malformed input (duplicate keys, NaN/Infinity, schema or
  cross-field violations, wrong release) raises a named error and leaves no
  partial state: documents are validated in full before the immutable result
  is built.
* **VAL-001** — :func:`decision_rule_hash` gives a stable hash of each
  registered decision rule, and loaded definitions are deeply immutable, so a
  registered rule cannot be altered in memory after loading.
* **IMP-003** — verification outcomes are emitted as structured audit events
  on the ``apgi.protocols`` logger.

The OpenTimestamps proof that anchors the manifest is not yet available
(``LOCK_ANCHOR`` below); see ``specifications/governance/deviations.yaml``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import pathlib
from types import MappingProxyType
from typing import Any, Mapping

import jsonschema

__all__ = [
    "ProtocolError",
    "ProtocolLockError",
    "ProtocolValidationError",
    "EXPECTED_PROTOCOL_IDS",
    "EXPECTED_RELEASE",
    "LOCK_ANCHOR",
    "default_protocols_dir",
    "verify_lock",
    "load_protocols",
    "load_protocol",
    "decision_rule_hash",
    "canonical_json",
]

EXPECTED_RELEASE = "1.1.0"
EXPECTED_PROTOCOL_IDS = tuple(f"APGI-P0{n}" for n in range(8))
LOCK_ANCHOR: Mapping[str, Any] = MappingProxyType(
    {"type": "OpenTimestamps", "proof": None, "status": "pending (DEV-0002)"}
)

_log = logging.getLogger("apgi.protocols")


class ProtocolError(Exception):
    """Base class for protocol loading failures."""

    code = "APGI-PROTOCOL-ERROR"


class ProtocolLockError(ProtocolError):
    """The definitions do not match the lock manifest (REP-001)."""

    code = "APGI-PROTOCOL-LOCK-MISMATCH"


class ProtocolValidationError(ProtocolError, ValueError):
    """A definition is malformed, incomplete or incompatible (PRO-002)."""

    code = "APGI-PROTOCOL-INVALID"


def _audit(event: str, **fields: Any) -> None:
    _log.info(json.dumps({"event": event, **fields}, sort_keys=True))


def default_protocols_dir() -> pathlib.Path:
    """``$APGI_PROTOCOLS_DIR`` if set, otherwise ``<repo>/protocols``."""
    env = os.environ.get("APGI_PROTOCOLS_DIR")
    if env:
        return pathlib.Path(env)
    return pathlib.Path(__file__).resolve().parents[2] / "protocols"


# ---------------------------------------------------------------------------
# Strict JSON
# ---------------------------------------------------------------------------


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise ProtocolValidationError(f"non-finite JSON number: {value}")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ProtocolValidationError(f"non-finite JSON number: {value}")
    return number


def _read_strict(raw: bytes, name: str) -> Any:
    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
    except ProtocolValidationError as exc:
        raise ProtocolValidationError(f"{name}: {exc}") from None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolValidationError(f"{name}: malformed JSON ({exc})") from None


def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON (sorted keys, no whitespace) used for hashing."""
    return json.dumps(
        _thaw(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


# ---------------------------------------------------------------------------
# Lock verification (REP-001)
# ---------------------------------------------------------------------------


def _safe_member(folder: pathlib.Path, name: str) -> pathlib.Path:
    path = (folder / name).resolve()
    if folder.resolve() not in path.parents:
        raise ProtocolLockError(f"manifest path escapes the protocol folder: {name}")
    return path


def verify_lock(folder: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Verify every manifest entry and return the lock record.

    The manifest must list each ``protocol_*.json`` present in *folder*, and
    every listed file must exist with the recorded SHA-256. Raises
    :class:`ProtocolLockError` on any discrepancy; reads nothing else.
    """
    root = pathlib.Path(folder) if folder is not None else default_protocols_dir()
    manifest_path = root / "MANIFEST.json"
    if not manifest_path.is_file():
        _audit("protocol_lock_failed", reason="manifest_missing", folder=str(root))
        raise ProtocolLockError(f"lock manifest not found: {manifest_path}")
    manifest_bytes = manifest_path.read_bytes()
    manifest = _read_strict(manifest_bytes, "MANIFEST.json")
    if manifest.get("release") != EXPECTED_RELEASE:
        raise ProtocolLockError(
            f"manifest release {manifest.get('release')!r} != expected {EXPECTED_RELEASE!r}"
        )
    entries = {entry["path"]: entry["sha256"] for entry in manifest.get("files", [])}
    problems: list[str] = []
    for name, expected in sorted(entries.items()):
        path = _safe_member(root, name)
        if not path.is_file():
            problems.append(f"missing: {name}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            problems.append(f"sha256 mismatch: {name}")
    for path in sorted(root.glob("protocol_*.json")):
        if path.name not in entries:
            problems.append(f"unlisted definition: {path.name}")
    if len([n for n in entries if n.startswith("protocol_")]) != len(EXPECTED_PROTOCOL_IDS):
        problems.append("manifest does not list exactly eight protocol definitions")
    if problems:
        _audit("protocol_lock_failed", folder=str(root), problems=problems)
        raise ProtocolLockError("protocol lock verification failed: " + "; ".join(problems))
    record = {
        "release": manifest["release"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "files": dict(sorted(entries.items())),
        "anchor": dict(LOCK_ANCHOR),
    }
    _audit("protocol_lock_verified", folder=str(root), manifest_sha256=record["manifest_sha256"])
    return record


# ---------------------------------------------------------------------------
# Validation and loading (PRO-002)
# ---------------------------------------------------------------------------


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _thaw(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_thaw(v) for v in value]
    return value


def _semantic_errors(data: Mapping[str, Any]) -> list[str]:
    errors = []
    people = data.get("participants", {})
    n_target = people.get("n_target")
    for key in ("n_minimum", "n_analyzable_target"):
        if people.get(key) is not None and n_target is not None and people[key] > n_target:
            errors.append(f"participants.{key} exceeds n_target")
    ids = [p.get("id") for p in data.get("sub_predictions", [])]
    if len(ids) != len(set(ids)):
        errors.append("duplicate sub_prediction id")
    if data.get("version") != EXPECTED_RELEASE:
        errors.append(f"version {data.get('version')!r} != {EXPECTED_RELEASE!r}")
    return errors


def load_protocols(
    folder: str | os.PathLike[str] | None = None,
) -> Mapping[str, Mapping[str, Any]]:
    """Verify the lock, validate every definition, and return them immutably.

    Returns a read-only mapping ``protocol_id -> definition``. Either all
    eight definitions load or an exception is raised; no partial set is
    ever returned.

    Raises:
        ProtocolLockError: lock manifest mismatch (nothing is parsed).
        ProtocolValidationError: malformed or incompatible definition.
    """
    root = pathlib.Path(folder) if folder is not None else default_protocols_dir()
    lock = verify_lock(root)
    schema_name = "schemas/protocol.schema.json"
    if schema_name not in lock["files"]:
        raise ProtocolLockError("protocol schema is not covered by the lock manifest")
    schema = _read_strict(_safe_member(root, schema_name).read_bytes(), schema_name)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, format_checker=jsonschema.FormatChecker())

    staged: dict[str, Any] = {}
    errors: list[str] = []
    for name in sorted(n for n in lock["files"] if n.startswith("protocol_")):
        path = _safe_member(root, name)
        data = _read_strict(path.read_bytes(), name)
        schema_errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        errors.extend(f"{name}: {e.message}" for e in schema_errors[:5])
        errors.extend(f"{name}: {msg}" for msg in _semantic_errors(data))
        pid = data.get("protocol_id")
        if pid in staged:
            errors.append(f"{name}: duplicate protocol_id {pid}")
        staged[pid] = data
    if set(staged) != set(EXPECTED_PROTOCOL_IDS):
        errors.append(f"protocol IDs {sorted(map(str, staged))} != {list(EXPECTED_PROTOCOL_IDS)}")
    if errors:
        _audit("protocol_validation_failed", errors=errors[:20])
        raise ProtocolValidationError("; ".join(errors))
    _audit("protocols_loaded", count=len(staged), manifest_sha256=lock["manifest_sha256"])
    return MappingProxyType({pid: _freeze(staged[pid]) for pid in EXPECTED_PROTOCOL_IDS})


def load_protocol(
    protocol_id: str, folder: str | os.PathLike[str] | None = None
) -> Mapping[str, Any]:
    """Load one definition — after verifying and validating the whole set."""
    protocols = load_protocols(folder)
    try:
        return protocols[protocol_id]
    except KeyError:
        raise ProtocolValidationError(f"unknown protocol_id {protocol_id!r}") from None


def decision_rule_hash(protocol: Mapping[str, Any], prediction_id: str) -> str:
    """SHA-256 of the canonical JSON of one registered sub-prediction rule."""
    for entry in protocol["sub_predictions"]:
        if entry["id"] == prediction_id:
            return hashlib.sha256(canonical_json(entry)).hexdigest()
    raise ProtocolValidationError(
        f"{protocol.get('protocol_id')}: no registered prediction {prediction_id!r}"
    )
