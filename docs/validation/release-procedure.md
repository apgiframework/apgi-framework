# Release procedure, rollback and certification — apgi-framework

APGI-VAL-SPEC-1.2 REL-001, REL-002, REL-004, REL-005 and §11. This is the
release package template; copy the checklist into the release notes of each
candidate.

## 1. Candidate identity (REL-001, IMP-001)

1. Pick a commit on `main` whose CI run (workflow **CI**, all jobs, including
   `reproducibility-macos`) passed.
2. Bump the version in `pyproject.toml` following
   `specifications/contracts/compatibility-policy.yaml`: MAJOR for any change
   to a scientific output, equation, boundary rule or schema meaning; MINOR
   for backward-compatible additions; PATCH otherwise.
3. Add the `CHANGELOG.md` section and a change record under
   `docs/validation/change-records/`.
4. Tag `vX.Y.Z`. The **Release** workflow re-runs the full CI workflow
   (`validate`), builds the sdist and wheel, and produces
   `release-manifest.json` with the artifact digests, protocol-lock hash,
   bundle digest, fixture index and schema hashes.
5. Publishing waits on the protected `pypi` environment. The release authority
   approves it only after the certification checklist (§4) is complete. That
   approval is the promotion record.

> The `pypi` environment's required-reviewer rule and branch protection on
> `main` are repository settings. They could not be inspected from the
> repository and must be confirmed by an administrator (XC-CI-01).

## 2. Deployment

A03 is a Python library and specification bundle; deployment means:

```bash
pip install apgi-framework==X.Y.Z
python -c "import apgi.protocols as p; p.load_protocols()"   # from a checkout
python scripts/build_spec_bundle.py --verify                  # consumers verify before use
```

## 3. Rollback (REL-002)

**Rollback criteria.** Roll back if any of these happens after release: a
fixture or protocol-lock gate fails on the released commit; a consumer reports a
checksum mismatch against `bundle/SHA256SUMS`; a defect of severity *critical*
or *high* is opened against a released scientific output; or the wheel's
digest differs from `release-manifest.json`.

**Procedure.**

1. Yank the release on PyPI (`pip` then stops resolving it by default) and
   mark the GitHub Release as superseded.
2. Consumers pin the previous version: `pip install "apgi-framework==<prev>"`.
3. Open a defect in `specifications/governance/deviations.yaml` that links
   the failing evidence.
4. Fix forward on a branch, re-run the full workflow and release a PATCH, or a
   MAJOR if the scientific output changes.

**Tabletop exercise.** Before the first certified release, rehearse steps 1–2
against a TestPyPI upload and record the result in the evidence index (not yet
done; see `docs/validation/task-status.yaml`, APGI-REL-002).

## 4. Certification checklist (§11; AUD-GOV-07)

| # | Check | Evidence in this repository | Current status |
|---|---|---|---|
| 1 | Release identity | `release-manifest.json` (Release workflow) | Mechanism in place; no certified candidate yet |
| 2 | Protocol lock | `apgi.protocols.verify_lock`, `tests/test_protocol_lock.py` | Pass; OpenTimestamps proof pending (DEV-0002) |
| 3 | Scientific conformance | fixtures, notation/terminology scans, claim register | Blocked: fixtures unapproved; DEV-0001, DEV-0003, DEV-0009 open |
| 4 | Reproducibility and deviations | `scripts/record_environment.py`, `scripts/verify_power.py`, `apgi.registration` | Partial: DEV-0004/0005/0007 open; macOS evidence pending |
| 5 | Data and API validation | profile, fixtures, `apgi.datasets.dataset_provenance` | Partial |
| 6 | Security | profile (no secrets, OIDC publishing) | No independent security review (Not appointed) |
| 7 | Cross-application integration | — | Blocked: other components not available (INT-002) |
| 8 | Version compatibility | `releases/compatibility-matrix.yaml` | Partial: only Linux/Python 3.11–3.12 tested |
| 9 | Release package and rollback | this document | Rollback tabletop not yet run |
| 10 | Change impact and regression | `docs/validation/change-records/` | CR-0001 recorded |
| 11 | Approvals | `specifications/governance/roles.yaml` | **Not appointed** — independence level: Self-attested |
| 12 | Archival gate | §5 below | Enforced by procedure; no deposit made |

Outcome today: **Not certified.**

## 5. Archival gate (REL-005)

No Zenodo/OSF deposit may be made for a release until its certificate exists.
The deposit must contain exactly the files listed in that release's
`release-manifest.json`, and their digests must be compared before the deposit
is published. `apgi-fetch` stays disabled (`DEPOSIT_STATUS = "not_deposited"`)
until a certified deposit holds the seed datasets.

## 6. Known limitations and monitoring

* Known limitations are the open entries in
  `specifications/governance/deviations.yaml`.
* Monitoring for a library means watching CI on `main` and the scheduled
  re-runs. Protocol-lock failures and validation failures are emitted as
  structured JSON events on the `apgi.protocols` logger, and every gate exits
  non-zero on failure (IMP-003).
