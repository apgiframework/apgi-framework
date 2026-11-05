"""AUD-GOV-02/03/06: profile completeness, roles and deviation-register hygiene."""

from __future__ import annotations

import datetime as dt
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
GOV = ROOT / "specifications" / "governance"
REQUIREMENTS = ["PRO-001", "PRO-002", "PRO-003", "PRO-004", "SCI-001", "SCI-002", "SCI-003", "SCI-004",
                "SCI-005", "SCI-006", "SCI-007", "REP-001", "REP-002", "REP-003", "REP-004", "REP-005",
                "IMP-001", "IMP-002", "IMP-003", "DAT-001", "DAT-002", "DAT-003", "DAT-004", "API-001",
                "API-002", "API-003", "API-004", "INT-001", "INT-002", "INT-003", "INT-004", "REL-001",
                "REL-002", "REL-003", "REL-004", "REL-005", "CON-001", "CON-002", "ACQ-001", "VAL-001",
                "CLI-001"]
MANDATORY = {"id", "requirement", "severity", "impact", "compensating_controls", "remediation", "owner",
             "approver", "status", "expiry"}


def test_profile_covers_every_requirement_with_rationale_for_exclusions():
    profile = yaml.safe_load((ROOT / "specifications/profile/application-validation-profile.yaml").read_text())
    applicability = profile["applicability"]
    assert sorted(applicability) == sorted(REQUIREMENTS)
    for req, entry in applicability.items():
        assert entry["decision"] in {"A", "N"}, req
        if entry["decision"] == "N":
            assert entry.get("rationale") and entry.get("approver"), req
        if entry["matrix"] == "R":
            assert entry["decision"] == "A", f"{req}: matrix R cannot be excluded"


def test_unfilled_roles_never_appear_as_approvals():
    roles = yaml.safe_load((GOV / "roles.yaml").read_text())
    assert roles["independence_level"] in {"Self-attested", "Independently reviewed"}
    deviations = yaml.safe_load((GOV / "deviations.yaml").read_text())["entries"]
    for d in deviations:
        assert MANDATORY <= set(d), d["id"]
        if d["approver"] == "Not appointed":
            assert d["status"] == "open", f"{d['id']} cannot be closed without an approver"


def test_no_expired_open_deviation():
    today = dt.date.today()
    for d in yaml.safe_load((GOV / "deviations.yaml").read_text())["entries"]:
        expiry = d["expiry"] if isinstance(d["expiry"], dt.date) else dt.date.fromisoformat(d["expiry"])
        assert d["status"] != "open" or expiry >= today, f"{d['id']} expired on {expiry}"
