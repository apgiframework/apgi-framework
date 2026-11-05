"""Registered-plan comparison and output labelling (APGI-VAL-SPEC-1.2 REP-004, VAL-001).

An analysis plan is compared field by field against the lock-verified
protocol definition. Anything that differs from, or is absent in, the
registered definition becomes a :class:`Deviation`; any deviation, any
non-confirmatory prediction status, and any unregistered model variant make
the output *exploratory*. :func:`label_output` stamps that decision — with
the registered rule hash and protocol lock hash — onto a result so it
propagates into every export path that serialises the result.

This module checks the machine-readable parts of a registration (prediction
IDs, status, alpha, sample size floor, model variant, declared steps). The
prose of ``primary_analysis`` cannot be checked automatically; a plan must
declare each step with ``registered: True`` and a source reference, and an
undeclared or unregistered step is a deviation.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from apgi.protocols import decision_rule_hash

__all__ = ["Deviation", "RegistrationCheck", "check_analysis", "label_output", "REGISTERED_VARIANT"]

REGISTERED_VARIANT = "MV-PROTOCOL-REDUCED-1"
_CONFIRMATORY = {"confirmatory"}


@dataclass(frozen=True)
class Deviation:
    """One departure from the registered protocol definition."""

    field: str
    registered: Any
    actual: Any
    message: str


@dataclass(frozen=True)
class RegistrationCheck:
    protocol_id: str
    prediction_id: str
    registered_status: str | None
    rule_sha256: str | None
    deviations: tuple[Deviation, ...] = field(default_factory=tuple)

    @property
    def confirmatory_eligible(self) -> bool:
        return not self.deviations and self.registered_status in _CONFIRMATORY

    @property
    def analysis_label(self) -> str:
        return "confirmatory" if self.confirmatory_eligible else "exploratory"


def _registered_alpha(protocol: Mapping[str, Any], prediction: Mapping[str, Any]) -> float | None:
    thresholds = prediction.get("confirming_thresholds") or {}
    if isinstance(thresholds, Mapping) and "alpha" in thresholds:
        return float(thresholds["alpha"])
    power = protocol.get("power_analysis") or {}
    alpha = power.get("alpha") if isinstance(power, Mapping) else None
    return float(alpha) if alpha is not None else None


def check_analysis(protocol: Mapping[str, Any], plan: Mapping[str, Any]) -> RegistrationCheck:
    """Compare an analysis *plan* with a registered *protocol* definition.

    Recognised plan keys: ``prediction_id`` (required), ``alpha``, ``n``,
    ``model_variant``, ``steps`` (list of mappings with ``name``,
    ``registered`` and optional ``source``), ``parameters`` (mapping of
    parameter overrides; any override is a deviation).
    """
    pid = str(protocol["protocol_id"])
    pred_id = str(plan.get("prediction_id"))
    deviations: list[Deviation] = []
    prediction = next((p for p in protocol["sub_predictions"] if p["id"] == pred_id), None)
    if prediction is None:
        deviations.append(Deviation("prediction_id", None, pred_id, "prediction is not registered"))
        return RegistrationCheck(pid, str(pred_id), None, None, tuple(deviations))

    alpha = _registered_alpha(protocol, prediction)
    if "alpha" in plan and (alpha is None or not math.isclose(float(plan["alpha"]), alpha, rel_tol=0, abs_tol=1e-12)):
        deviations.append(Deviation("alpha", alpha, plan["alpha"], "alpha differs from registration"))
    floor = (protocol.get("participants") or {}).get("n_minimum")
    if "n" in plan and floor is not None and int(plan["n"]) < int(floor):
        deviations.append(Deviation("n", floor, plan["n"], "sample size below registered minimum"))
    variant = plan.get("model_variant", REGISTERED_VARIANT)
    if variant != REGISTERED_VARIANT:
        deviations.append(Deviation("model_variant", REGISTERED_VARIANT, variant,
                                    "model formulation differs from the registered reduced specification"))
    for step in plan.get("steps", []):
        if not step.get("registered", False):
            deviations.append(Deviation("steps", None, step.get("name"), "unregistered analysis step"))
    for name, value in (plan.get("parameters") or {}).items():
        deviations.append(Deviation(f"parameters.{name}", "registered value", value,
                                    "parameter override not in registration"))
    return RegistrationCheck(
        protocol_id=pid,
        prediction_id=pred_id,
        registered_status=prediction.get("status"),
        rule_sha256=decision_rule_hash(protocol, pred_id),
        deviations=tuple(deviations),
    )


def label_output(result: Mapping[str, Any], check: RegistrationCheck,
                 lock: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a copy of *result* carrying the registration label and lineage.

    The label is written under the ``registration`` key and mirrored in
    ``analysis_label`` at top level so that any exporter which serialises
    the result keeps it. An output that already claims ``confirmatory``
    while the check says otherwise is downgraded, never upgraded.
    """
    labelled = dict(result)
    labelled["analysis_label"] = check.analysis_label
    labelled["registration"] = {
        "protocol_id": check.protocol_id,
        "prediction_id": check.prediction_id,
        "registered_status": check.registered_status,
        "rule_sha256": check.rule_sha256,
        "protocol_manifest_sha256": (lock or {}).get("manifest_sha256"),
        "confirmatory_eligible": check.confirmatory_eligible,
        "deviations": [asdict(d) for d in check.deviations],
    }
    return labelled
