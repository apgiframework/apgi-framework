"""TC-SCI-03: canonical L0–L4 boundaries, just-outside values and label inventory."""

import math
import pathlib

import pytest
import yaml

from apgi.hierarchy_levels import LEVELS, classify_timescale, level_bounds

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIN, HOUR, DAY = 60.0, 3600.0, 86400.0


@pytest.mark.parametrize("seconds,expected", [
    (0.010, ("L0",)), (0.050, ("L0",)), (0.100, ("L0", "L1")), (1.0, ("L1",)), (3.0, ("L1",)),
    (1 * MIN, ("L2",)), (30 * MIN, ("L2",)), (1 * HOUR, ("L3",)), (5 * DAY, ("L3",)),
    (60 * DAY, ("L4",)), (5 * 365.25 * DAY, ("L4",)),
])
def test_values_at_and_inside_bounds(seconds, expected):
    assert classify_timescale(seconds) == expected


@pytest.mark.parametrize("seconds", [
    math.nextafter(0.010, 0), math.nextafter(3.0, math.inf), math.nextafter(60.0, 0),
    math.nextafter(1800.0, math.inf), math.nextafter(3600.0, 0), 20 * DAY, 11 * 365.25 * DAY,
])
def test_values_just_outside_are_unassigned(seconds):
    assert classify_timescale(seconds) == ()


@pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf])
def test_invalid_timescales_raise(bad):
    with pytest.raises(ValueError):
        classify_timescale(bad)


def test_code_matches_specification_yaml():
    spec = yaml.safe_load((ROOT / "specifications/model/temporal-hierarchy.yaml").read_text())
    assert [lv["id"] for lv in spec["levels"]] == [lv.id for lv in LEVELS] == ["L0", "L1", "L2", "L3", "L4"]
    for lv in spec["levels"]:
        assert level_bounds(lv["id"]) == pytest.approx((lv["lower_s"], lv["upper_s"]))
    with pytest.raises(KeyError):
        level_bounds("L5")


def test_legacy_hierarchy_is_not_labelled_canonical():
    """The exploratory processing hierarchy must not claim L0–L4 labels."""
    import re

    source = (ROOT / "src/apgi/extensions/hierarchical.py").read_text()
    assert not re.search(r"\bL[0-5]\b", source)
