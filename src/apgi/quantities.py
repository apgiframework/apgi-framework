"""Kind-safe scalar types for precision (Π) and prediction-error magnitude (|ε|, z).

Registry tasks S1-REG-02 / S1-FIX-05 (APGI-VAL-SPEC-1.2, SCI-004).

The core equation Sₜ = Πᵉ·|zᵉ| + Πⁱ_eff·|zⁱ| is a sum of *precision × error*
products. Two category errors recur across consumers and must be impossible
to express silently:

* ``Precision × Precision`` — squares a gain and has no meaning in Eq. 1.
* ``PEM × PEM`` — squares an error (a variance-like quantity), which is the
  half-weighted squared-error formulation the specification rejects.

Static typing alone cannot enforce this (``NewType`` aliases erase at
runtime), so :class:`Precision` and :class:`PredictionError` are thin
``float`` subclasses that raise :class:`QuantityKindError` on the forbidden
products while leaving every other float operation untouched. The product of
a precision and an error is returned as a plain ``float`` — the weighted
surprise contribution — so downstream arithmetic is unaffected.

These types are opt-in: the core functions in :mod:`apgi.core` accept plain
floats and remain numerically identical when given these subclasses.
"""

from __future__ import annotations

import math
from typing import NewType

__all__ = [
    "QuantityKindError",
    "Precision",
    "PredictionError",
    "PEM",
    "PrecisionValue",
    "PEMValue",
    "weighted_error",
]

# Static aliases for annotation-only use (erased at runtime).
PrecisionValue = NewType("PrecisionValue", float)
PEMValue = NewType("PEMValue", float)


class QuantityKindError(TypeError):
    """Raised when two quantities of an incompatible kind are combined."""


def _kind(value: object) -> str | None:
    if isinstance(value, Precision):
        return "precision"
    if isinstance(value, PredictionError):
        return "prediction_error"
    return None


class _KindedFloat(float):
    """Common base: finite check and kind-aware multiplication."""

    KIND = "abstract"

    def __new__(cls, value: float) -> _KindedFloat:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f"{cls.__name__} must be finite, got {value!r}")
        return super().__new__(cls, number)

    def _check(self, other: object, op: str) -> None:
        other_kind = _kind(other)
        if other_kind is not None and other_kind == self.KIND:
            raise QuantityKindError(
                f"{self.KIND} {op} {other_kind} is not a defined APGI quantity "
                "(Eq. 1 weights each error by exactly one precision)."
            )

    def __mul__(self, other: object) -> float:  # type: ignore[override]
        self._check(other, "*")
        return float(self) * float(other)  # type: ignore[arg-type]

    def __rmul__(self, other: object) -> float:  # type: ignore[override]
        self._check(other, "*")
        return float(other) * float(self)  # type: ignore[arg-type]

    def __pow__(self, other: object, mod: object = None) -> float:  # type: ignore[override]
        if mod is None and float(other) == 2.0:  # type: ignore[arg-type]
            raise QuantityKindError(
                f"squaring a {self.KIND} is a {self.KIND} * {self.KIND} product"
            )
        return float(self) ** float(other)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({float(self)!r})"


class Precision(_KindedFloat):
    """Precision (inverse-variance gain) Π; must be non-negative."""

    KIND = "precision"

    def __new__(cls, value: float) -> Precision:
        obj = super().__new__(cls, value)
        if float(obj) < 0:
            raise ValueError(f"Precision must be non-negative, got {value!r}")
        return obj  # type: ignore[return-value]


class PredictionError(_KindedFloat):
    """Standardized prediction error z (signed); use ``abs()`` for |z|."""

    KIND = "prediction_error"

    def __abs__(self) -> PredictionError:
        return PredictionError(abs(float(self)))

    def __neg__(self) -> PredictionError:
        return PredictionError(-float(self))


PEM = PredictionError  # registry short name: prediction-error magnitude


def weighted_error(pi: Precision, z: PredictionError) -> float:
    """Return Π·|z| after checking both operand kinds explicitly."""
    if not isinstance(pi, Precision):
        raise QuantityKindError(f"expected Precision, got {type(pi).__name__}")
    if not isinstance(z, PredictionError):
        raise QuantityKindError(f"expected PredictionError, got {type(z).__name__}")
    return pi * abs(z)
