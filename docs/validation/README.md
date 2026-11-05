# APGI-VAL-SPEC-1.2 validation — apgi-framework (A03)

This directory holds the planning, release and review records that
APGI-VAL-SPEC-1.2 (§9) requires for this component. The machine-readable
authority data lives in `specifications/`, `fixtures/`, `traceability/`,
`gates/` and `releases/`; the checksums for all of it are in
`bundle/SHA256SUMS`.

**Status: not certified.** Every role except automated CI reads "Not
appointed" (`specifications/governance/roles.yaml`). Everything here is
self-attested, and no decision has been approved.

## Where things are

| Need | File |
|---|---|
| Application Validation Profile, applicability, NOT_APPLICABLE rationales | `specifications/profile/application-validation-profile.yaml` |
| Parameter / state / signal registry (IDs, kinds, units, provenance, scope layer) | `specifications/model/parameter-registry.yaml` |
| Equations, observables, decision rules (rule hashes) | `specifications/model/*.yaml` |
| Model variants (registered vs exploratory) | `specifications/model-variants/` |
| Canonical L0–L4 hierarchy | `specifications/model/temporal-hierarchy.yaml`, `apgi.hierarchy_levels` |
| Notation map | `specifications/notation/symbol-map.yaml` |
| Claim register (CLM-nnnn) | `specifications/claims/claim-register.yaml` |
| Prediction ↔ equation ↔ code ↔ protocol ↔ evidence | `traceability/` |
| Golden fixtures (independent 60-digit decimal) | `fixtures/` |
| Gate table and exposable fields | `gates/` |
| Compatibility policy and matrix | `specifications/contracts/compatibility-policy.yaml`, `releases/compatibility-matrix.yaml` |
| Release manifest schema | `releases/release-manifest.schema.json` |
| Defects and deviations, risks, roles, sources | `specifications/governance/` |
| Evidence index | `docs/validation/evidence-index.yaml` |
| Task-by-task status against the supplied registers | `docs/validation/task-status.yaml` |
| Release procedure, rollback, certification gates | `docs/validation/release-procedure.md` |
| Change records (REL-003) | `docs/validation/change-records/` |

## Running every gate locally

```bash
make validate-all
```

This runs the same checks as CI: protocol lock, fixtures `--check`, registry
and bundle drift, notation and terminology scans, independent power
reproduction, gate-table schema, release manifest and the full test suite.

## Regenerating derived files after an authority-data change

```bash
make specs
```

The target regenerates fixtures, derived registries/traceability and the
bundle checksums, in that order. Review the diff and record a change record
before committing.
