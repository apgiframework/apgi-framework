# Model variants

One file per registered or exploratory model formulation (task S1-FWK-09,
APGI-VAL-SPEC-1.2 SCI-002). Formulations are **not numerically
interchangeable**: conformance means matching the fixtures for the declared
variant. Every variant declares its status:

| Variant | Status | Code |
|---|---|---|
| `MV-CORE-DISCRETE-1` | registered (draft — pending scientific-authority approval) | `apgi.core` |
| `MV-PROTOCOL-REDUCED-1` | registered in protocol definitions; **not implemented** in `src/apgi` | — |
| `MV-HIERARCHICAL-EXT-1` | exploratory | `apgi.extensions.hierarchical` |
| `MV-LNN-EXT-1` | exploratory | `apgi.extensions.liquid_network` |
| `MV-SAMPLE-DOC-1` | exploratory / illustrative (legacy three-group generator) | `apgi.datasets.make_sample_doc_groups` |

`apgi.model_variants.require_variant()` raises `UnregisteredVariantError`
when code asks for an unknown variant, and returns the variant record (with
its status) otherwise, so an alternative model can only ever run labelled
(task S1-PR2-03).
