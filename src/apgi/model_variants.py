"""Registered and exploratory model variants (S1-FWK-09, S1-PR2-03, SCI-002).

Mirror of ``specifications/model-variants/*.yaml`` (a test keeps the two in
sync). Code that runs a formulation other than the registered core model
must obtain its record through :func:`require_variant`; unknown variants
raise, and every returned record carries its status so results can be
labelled (``confirmatory_eligible`` is False for anything not registered).
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

__all__ = [
    "UnregisteredVariantError",
    "VARIANTS",
    "REGISTERED_STATUSES",
    "require_variant",
    "label_for",
    "UnmappedParameterError",
    "PROTOCOL_TO_CORE_MAPPING",
    "map_parameters",
]

REGISTERED_STATUSES = frozenset({"registered_draft", "registered"})


class UnregisteredVariantError(LookupError):
    """Raised when code requests a model variant absent from the registry."""


def _record(**fields: object) -> Mapping[str, object]:
    return MappingProxyType(dict(fields))


VARIANTS: Mapping[str, Mapping[str, object]] = MappingProxyType(
    {
        "MV-CORE-DISCRETE-1": _record(
            model_version="1.0.0", status="registered_draft", code="apgi.core"
        ),
        "MV-PROTOCOL-REDUCED-1": _record(
            model_version="1.1.0",
            status="registered_in_protocols_not_implemented",
            code=None,
        ),
        "MV-HIERARCHICAL-EXT-1": _record(
            model_version="0.1.0", status="exploratory", code="apgi.extensions.hierarchical"
        ),
        "MV-LNN-EXT-1": _record(
            model_version="0.1.0", status="exploratory", code="apgi.extensions.liquid_network"
        ),
        "MV-SAMPLE-DOC-1": _record(
            model_version="0.1.0",
            status="exploratory_illustrative",
            code="apgi.datasets.make_sample_doc_groups",
        ),
    }
)


def require_variant(variant_id: str, model_version: str | None = None) -> Mapping[str, object]:
    """Return the registry record for *variant_id* or raise.

    Args:
        variant_id: Registry ID, e.g. ``"MV-CORE-DISCRETE-1"``.
        model_version: If given, must equal the registered model version;
            a mismatch raises (explicit migration is required, S1-FIX-07.6).

    Raises:
        UnregisteredVariantError: unknown ID or incompatible model version.
    """
    try:
        record = VARIANTS[variant_id]
    except KeyError:
        raise UnregisteredVariantError(
            f"model variant {variant_id!r} is not registered; register it in "
            "specifications/model-variants/ or run a registered variant"
        ) from None
    if model_version is not None and model_version != record["model_version"]:
        raise UnregisteredVariantError(
            f"{variant_id} model_version {model_version!r} is not the registered "
            f"version {record['model_version']!r}; migrate explicitly"
        )
    return record


def label_for(variant_id: str) -> dict[str, object]:
    """Output label for results produced by *variant_id* (REP-004)."""
    record = require_variant(variant_id)
    status = str(record["status"])
    eligible = status in REGISTERED_STATUSES
    return {
        "model_variant": variant_id,
        "model_version": record["model_version"],
        "variant_status": status,
        "confirmatory_eligible": eligible,
        "analysis_label": "registered" if eligible else "exploratory",
    }


class UnmappedParameterError(KeyError):
    """A parameter has no registered mapping into the target variant."""


# Versioned mapping MV-PROTOCOL-REDUCED-1 (protocol JSON names) ->
# MV-CORE-DISCRETE-1 keyword arguments (S1-PR2-01). ``None`` marks a
# parameter that is registered but has no core-model counterpart.
PROTOCOL_TO_CORE_MAPPING: Mapping[str, object] = MappingProxyType(
    {
        "mapping_version": "0.1.0",
        "theta_0": ("theta_0", "PAR-THETA-0"),
        "gamma_sig": ("gamma_sig", "PAR-GAMMA-SIG"),
        "beta_SM": ("beta_sm", "PAR-BETA-SM"),
        "Pi_e": ("pi_e", "PAR-PI-E"),
        "Pi_i": ("pi_i_baseline", "PAR-PI-I-BASELINE"),
        "tau_S": ("tau_S", "PAR-TAU-S"),
        "tau_theta": ("lambda_theta", "PAR-LAMBDA-THETA"),
        "eta": None,
        "rho": None,
    }
)


def map_parameters(
    params: Mapping[str, float],
    *,
    step_seconds: float | None = None,
    allow_alternative: bool = False,
) -> dict[str, object]:
    """Map protocol reduced-specification parameters onto the core model.

    Unit conversions are explicit: ``tau_S`` and ``tau_theta`` are seconds in
    the protocols, so *step_seconds* (the physical duration of one core-model
    step) is required to convert them (τ_S → τ_S/step, τ_θ → λ_θ = step/τ_θ).

    Silent substitution is impossible (S1-PR2-03): a parameter without a
    core counterpart raises :class:`UnmappedParameterError` unless
    *allow_alternative* is True, in which case the run is returned labelled
    as the alternative model ``MV-PROTOCOL-REDUCED-1`` with the unmapped
    names listed. Either way ``confirmatory_eligible`` is False, because the
    core model is not the protocols' registered formulation.

    Returns:
        dict with ``kwargs`` (core keyword arguments), ``registry_ids``,
        ``unmapped`` and a REP-004 ``label``.
    """
    kwargs: dict[str, float] = {}
    key: str
    reg_id: str
    registry_ids: dict[str, str] = {}
    unmapped: list[str] = []
    for name, value in params.items():
        if name not in PROTOCOL_TO_CORE_MAPPING or name == "mapping_version":
            raise UnmappedParameterError(f"parameter {name!r} is not in the registered mapping")
        target = PROTOCOL_TO_CORE_MAPPING[name]
        if target is None:
            unmapped.append(name)
            continue
        key, reg_id = target  # type: ignore[misc]
        key, reg_id = str(key), str(reg_id)
        number = float(value)
        if name in ("tau_S", "tau_theta"):
            if step_seconds is None or step_seconds <= 0:
                raise ValueError(f"{name} is in seconds; pass a positive step_seconds to convert it")
            number = number / step_seconds if name == "tau_S" else step_seconds / number
        kwargs[key] = number
        registry_ids[key] = reg_id
    if unmapped and not allow_alternative:
        raise UnmappedParameterError(
            f"no MV-CORE-DISCRETE-1 counterpart for {sorted(unmapped)}; pass "
            "allow_alternative=True to run as a labelled alternative model"
        )
    variant = "MV-PROTOCOL-REDUCED-1" if unmapped else "MV-CORE-DISCRETE-1"
    label = label_for(variant)
    # The core discrete model is a different formulation from the protocols'
    # reduced specification (MV-PROTOCOL-REDUCED-1), so any protocol analysis
    # run through this mapping is a registered-plan deviation (REP-004).
    label["confirmatory_eligible"] = False
    label["analysis_label"] = "exploratory"
    label["deviation"] = (
        "protocol parameters evaluated with MV-CORE-DISCRETE-1, not the registered "
        "MV-PROTOCOL-REDUCED-1 formulation"
    )
    return {
        "kwargs": kwargs,
        "registry_ids": registry_ids,
        "unmapped": sorted(unmapped),
        "mapping_version": PROTOCOL_TO_CORE_MAPPING["mapping_version"],
        "label": label,
    }
