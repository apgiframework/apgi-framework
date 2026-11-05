"""Canonical five-level APGI temporal hierarchy (APGI-VAL-SPEC-1.2 SCI-003).

    L0  10 ms – 100 ms
    L1  100 ms – 3 s
    L2  1 min – 30 min
    L3  hours – days
    L4  months – years

Machine-readable source: ``specifications/model/temporal-hierarchy.yaml``.
The L3/L4 numeric bounds below ("hours–days" → 1 h – 10 d; "months–years" →
30 d – 10 y) are a draft operationalisation pending scientific-authority
confirmation (DEV-0003). The canonical hierarchy is a *timescale*
classification; the processing levels of
:class:`apgi.extensions.hierarchical.APGIHierarchy` are a separate,
exploratory model and are not labelled L0–L4.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = ["TimescaleLevel", "LEVELS", "classify_timescale", "level_bounds"]

_MINUTE = 60.0
_HOUR = 3600.0
_DAY = 86400.0
_YEAR = 365.25 * _DAY


@dataclass(frozen=True)
class TimescaleLevel:
    """One canonical hierarchy level with closed bounds in seconds."""

    id: str
    lower_s: float
    upper_s: float
    description: str

    def contains(self, seconds: float) -> bool:
        return self.lower_s <= seconds <= self.upper_s


LEVELS: tuple[TimescaleLevel, ...] = (
    TimescaleLevel("L0", 0.010, 0.100, "10–100 ms"),
    TimescaleLevel("L1", 0.100, 3.0, "100 ms–3 s"),
    TimescaleLevel("L2", 1 * _MINUTE, 30 * _MINUTE, "1–30 min"),
    TimescaleLevel("L3", 1 * _HOUR, 10 * _DAY, "hours–days"),
    TimescaleLevel("L4", 30 * _DAY, 10 * _YEAR, "months–years"),
)


def level_bounds(level_id: str) -> tuple[float, float]:
    """Return the (lower, upper) bounds in seconds for a level ID."""
    for level in LEVELS:
        if level.id == level_id:
            return level.lower_s, level.upper_s
    raise KeyError(f"unknown hierarchy level {level_id!r}; expected one of L0–L4")


def classify_timescale(seconds: float) -> tuple[str, ...]:
    """Return every canonical level whose closed interval contains *seconds*.

    * A value inside exactly one level returns a 1-tuple, e.g. ``("L1",)``.
    * The shared L0/L1 boundary (0.1 s) returns ``("L0", "L1")`` — the
      ambiguity is surfaced, never resolved silently.
    * A value outside every level (below 10 ms, in a gap such as 3 s–60 s,
      or above the L4 bound) returns ``()``; callers must treat it as
      unassigned rather than defaulting to a level.

    Raises:
        ValueError: if *seconds* is not finite or is not positive.
    """
    value = float(seconds)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"timescale must be a finite positive number of seconds, got {seconds!r}")
    return tuple(level.id for level in LEVELS if level.contains(value))
