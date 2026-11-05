"""S1-REG-02 / S1-FIX-05: Precision×Precision and PEM×PEM raise."""

import math

import pytest

from apgi.core import compute_S_t
from apgi.quantities import PEM, Precision, PredictionError, QuantityKindError, weighted_error


def test_precision_times_precision_raises():
    with pytest.raises(QuantityKindError):
        Precision(1.2) * Precision(0.9)


def test_pem_times_pem_raises():
    with pytest.raises(QuantityKindError):
        PredictionError(0.8) * PEM(0.5)
    with pytest.raises(QuantityKindError):
        PredictionError(0.8) ** 2


def test_precision_squared_raises():
    with pytest.raises(QuantityKindError):
        Precision(2.0) ** 2


def test_precision_times_error_is_weighted_error():
    value = Precision(1.2) * abs(PredictionError(-0.8))
    assert type(value) is float and value == pytest.approx(0.96)
    assert weighted_error(Precision(0.9), PredictionError(-0.5)) == pytest.approx(0.45)


def test_kinded_values_flow_through_core_unchanged():
    assert compute_S_t(Precision(1.2), PredictionError(-0.8), Precision(0.9), PredictionError(-0.5)) == \
        pytest.approx(1.41)


def test_domain_checks():
    with pytest.raises(ValueError):
        Precision(-0.1)
    with pytest.raises(ValueError):
        PredictionError(math.nan)
    with pytest.raises(QuantityKindError):
        weighted_error(PredictionError(1.0), PredictionError(1.0))  # type: ignore[arg-type]
    with pytest.raises(QuantityKindError):
        weighted_error(Precision(1.0), Precision(1.0))  # type: ignore[arg-type]


def test_plain_float_arithmetic_unaffected():
    assert Precision(2.0) * 3.0 == 6.0
    assert 3.0 * PredictionError(2.0) == 6.0
    assert repr(Precision(1.5)) == "Precision(1.5)"
    assert -PredictionError(1.0) == PredictionError(-1.0)
