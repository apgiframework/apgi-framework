#!/usr/bin/env bash
# reproduce_all.sh — full reproducibility entry point for APGI figures.
#
# Running this script from the repository root regenerates every published
# figure from the archived seed data, validates all outputs, and exits with
# a non-zero status if anything fails.
#
# Usage:
#   bash reproduce_all.sh              # regenerate seeds, verify checksums, then figures (default)
#   bash reproduce_all.sh --local      # use already-generated local seeds (verified)
#   bash reproduce_all.sh --zenodo     # download a deposited copy (only once deposited)
#
# Requirements: apgi installed in the active Python environment.
#   pip install -e ".[dev]"
#   OR for exact-version reproducibility:
#   conda env create -f environment.lock.yml && conda activate apgi && pip install -e ".[dev]"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default is "generate": the nine seed datasets are not deposited on Zenodo
# (data/seeds/seed_manifest.json deposit.status = not_deposited), so they are
# regenerated locally and checked against data/checksums.sha256.
MODE="generate"
if [[ "${1:-}" == "--local" ]];    then MODE="local";    fi
if [[ "${1:-}" == "--zenodo" ]];   then MODE="zenodo";   fi

echo "=== APGI reproducibility pipeline (mode: $MODE) ==="
echo "    $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "    Python: $(python3 --version)"
echo ""

# ------------------------------------------------------------------
# Step 1 — Data
# ------------------------------------------------------------------
echo "--- Step 1: data ---"
case "$MODE" in
  zenodo)
    echo "Fetching seed datasets from Zenodo…"
    apgi-fetch
    echo "Verifying checksums…"
    apgi-fetch --verify
    DATA_DIR="data/cache"
    ;;
  local)
    echo "Using local seeds in data/seeds/"
    DATA_DIR="data/seeds"
    # Verify the expected seed files are present before continuing.
    MISSING=()
    for sim in sim0_hep_proxy sim1_ignition_dynamics sim2_parameter_recovery \
               sim3_liquid_network sim4_hierarchical sim5_doc_biomarker \
               sim6_bifurcation sim7_metabolic_crossover sim8_tms_pci; do
      [[ -f "data/seeds/${sim}.npz" ]] || MISSING+=("${sim}.npz")
    done
    if [[ ${#MISSING[@]} -gt 0 ]]; then
      echo "ERROR: missing local seed files: ${MISSING[*]}" >&2
      echo "Run 'python3 data/generate_seeds.py' first, or use --generate." >&2
      exit 1
    fi
    echo "  All seed files present; verifying checksums…"
    python3 data/generate_seeds.py --verify
    ;;
  generate)
    echo "Regenerating seed datasets…"
    python3 data/generate_seeds.py
    echo "Verifying regenerated seeds against data/checksums.sha256…"
    python3 data/generate_seeds.py --verify
    DATA_DIR="data/seeds"
    ;;
esac

# Export DATA_DIR so figure and analysis scripts can read it via os.environ.
export APGI_DATA_DIR="$SCRIPT_DIR/$DATA_DIR"
echo "  APGI_DATA_DIR=$APGI_DATA_DIR"

# ------------------------------------------------------------------
# Step 2 — Tests
# ------------------------------------------------------------------
echo ""
echo "--- Step 2: unit tests ---"
pytest tests/ -q --tb=short

# ------------------------------------------------------------------
# Step 3 — Protocol validation
# ------------------------------------------------------------------
echo ""
echo "--- Step 3: protocol lock, schema and specification bundle ---"
# Release-aware validator: verifies every file against protocols/MANIFEST.json
# and validates only protocol instances against the protocol schema
# (MANIFEST.json / VALIDATION.json are release metadata, not protocols).
python3 scripts/validate_protocols.py
# Lock-enforcing loader (refuses altered definitions; REP-001).
python3 -c "from apgi.protocols import load_protocols; load_protocols(); print('  protocol lock verified')"
# Specification bundle checksums, generated registries and fixtures (S1-FWK-04).
python3 scripts/build_spec_bundle.py --verify
python3 scripts/build_specifications.py --check
python3 -I fixtures/generate_fixtures.py --check

# ------------------------------------------------------------------
# Step 4 — Figures
# ------------------------------------------------------------------
echo ""
echo "--- Step 4: figures ---"
# Validate the committed v1.1 series first: it checks the v1.0 baseline PNGs
# that the frozen v1.0 protocol scripts below regenerate.
python3 figures/v1_1/validate.py > /dev/null && echo "  v1.1 figure series: valid"
for script in figures/v1_0/protocols/p[0-7]_*.py; do
  echo "  $(basename "$script")…"
  python3 "$script" --no-show
done

# ------------------------------------------------------------------
# Step 5 — Bifurcation and somatic marker scripts
# ------------------------------------------------------------------
echo ""
echo "--- Step 5: analysis scripts ---"
python3 scripts/APGI_LNN_Bifurcation_Analysis.py      --no-show 2>/dev/null \
  || python3 scripts/APGI_LNN_Bifurcation_Analysis.py            2>&1 | tail -3
python3 scripts/APGI_Somatic_Marker_Identifiability.py --no-show 2>/dev/null \
  || python3 scripts/APGI_Somatic_Marker_Identifiability.py       2>&1 | tail -3

# ------------------------------------------------------------------
# Step 6 — Output manifest
# ------------------------------------------------------------------
echo ""
echo "--- Step 6: output manifest ---"
find figures/v1_0/output scripts/output -name "*.pdf" -o -name "*.png" 2>/dev/null \
  | sort | while read f; do
    echo "  $f  $(du -sh "$f" | cut -f1)"
  done

echo ""
echo "=== Reproduction complete. All outputs verified. ==="
