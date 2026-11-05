"""INT-003: upstream failures propagate as defined errors, never as silent defaults."""

import math
from unittest.mock import patch

import numpy as np
import pytest

from apgi import core, parameter_recovery
from apgi.integration import APGICoreIntegration


def test_recovery_raises_on_non_finite_objective():
    data = parameter_recovery.generate_synthetic_data(20, 0.5, 5.0, 1.0, 0.6, 5.0, seed=1)
    with patch.object(parameter_recovery, "_negative_log_likelihood", return_value=math.nan):
        with pytest.raises(RuntimeError, match="non-finite"):
            parameter_recovery.recover_parameters(data, n_restarts=1)


def test_integration_propagates_invalid_input():
    integ = APGICoreIntegration()
    with pytest.raises(ValueError):
        integ.step(pi_e=1.0, z_e=float("nan"), pi_i_baseline=1.0, z_i=0.5, C_t=1.0, I_t=0.5)
    assert integ._records == []  # no partial record appended


def test_nan_never_becomes_a_probability():
    with pytest.raises(ValueError):
        core.ignition_probability(np.nan, 0.5)


@pytest.mark.parametrize("bad", [{"NE_t": float("nan")}, {"C_t": float("inf")}, {"I_t": float("nan")}])
def test_rejected_trial_leaves_session_state_unchanged(bad):
    """PRO-002: an input rejected late in the trial must not leave a partial record."""
    integ = APGICoreIntegration(theta_init=0.6)
    integ.step(1.0, 1.0, 1.0, 1.0, 1.0, 0.5)
    snapshot = (len(integ._records), integ._S_acc, integ._theta)
    kwargs = {"C_t": 1.0, "I_t": 0.5, "NE_t": 0.0, **bad}
    with pytest.raises(ValueError):
        integ.step(1.0, 1.0, 1.0, 1.0, **kwargs)
    assert (len(integ._records), integ._S_acc, integ._theta) == snapshot
