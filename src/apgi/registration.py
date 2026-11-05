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


def _registered_alphas(protocol: Mapping[str, Any], prediction: Mapping[str, Any]) -> dict[str, float]:
    """Every registered alpha for *prediction*, keyed by its registered field name.

    Predictions register test-specific levels (``alpha``, ``alpha_two_tailed``,
    ``permutation_alpha``, ``dip_alpha`` …) in ``confirming_thresholds``; the
    protocol-level ``power_analysis.alpha`` applies only when a prediction
    registers none.
    """
    thresholds = prediction.get("confirming_thresholds") or {}
    found: dict[str, float] = {}
    if isinstance(thresholds, Mapping):
        for key, value in thresholds.items():
            if "alpha" in key and isinstance(value, (int, float)) and not isinstance(value, bool):
                found[key] = float(value)
    if not found:
        power = protocol.get("power_analysis") or {}
        alpha = power.get("alpha") if isinstance(power, Mapping) else None
        if alpha is not None:
            found["power_analysis.alpha"] = float(alpha)
    return found


def check_analysis(protocol: Mapping[str, Any], plan: Mapping[str, Any]) -> RegistrationCheck:
    """Compare an analysis *plan* with a registered *protocol* definition.

    Recognised plan keys: ``prediction_id`` (required), ``alpha`` (with
    optional ``alpha_field`` naming the registered threshold, e.g.
    ``"permutation_alpha"``), ``n``,
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

    alphas = _registered_alphas(protocol, prediction)
    if "alpha" in plan:
        wanted = plan.get("alpha_field")
        candidates = {wanted: alphas[wanted]} if wanted in alphas else alphas
        if wanted is not None and wanted not in alphas:
            deviations.append(Deviation("alpha_field", sorted(alphas), wanted,
                                        "alpha field is not registered for this prediction"))
        elif not any(math.isclose(float(plan["alpha"]), a, rel_tol=0, abs_tol=1e-12)
                     for a in candidates.values()):
            deviations.append(Deviation("alpha", alphas or None, plan["alpha"],
                                        "alpha differs from registration"))
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
    prior = result.get("analysis_label")
    # A result already exploratory for another reason (dataset, model variant,
    # provenance) stays exploratory; this check can only downgrade.
    upstream_exploratory = prior is not None and prior != "confirmatory"
    eligible = check.confirmatory_eligible and not upstream_exploratory
    labelled["analysis_label"] = "confirmatory" if eligible else "exploratory"
    labelled["registration"] = {
        "protocol_id": check.protocol_id,
        "prediction_id": check.prediction_id,
        "registered_status": check.registered_status,
        "rule_sha256": check.rule_sha256,
        "protocol_manifest_sha256": (lock or {}).get("manifest_sha256"),
        "confirmatory_eligible": eligible,
        "prior_analysis_label": prior,
        "deviations": [asdict(d) for d in check.deviations],
    }
    return labelled
