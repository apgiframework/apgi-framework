#!/usr/bin/env bash
# Anchor the protocol lock manifest with OpenTimestamps (REP-001, DEV-0002).
#
# Run by the specification owner, not by CI: stamping submits the manifest's
# SHA-256 digest (not its content) to public OpenTimestamps calendars.
#
#   pip install opentimestamps-client
#   bash scripts/anchor_protocol_lock.sh            # create protocols/MANIFEST.json.ots
#   bash scripts/anchor_protocol_lock.sh --upgrade  # after ~1 day: attach the Bitcoin attestation
#   bash scripts/anchor_protocol_lock.sh --verify
#
# Then commit protocols/MANIFEST.json.ots, set LOCK_ANCHOR in
# src/apgi/protocols.py to reference it, and close DEV-0002.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python3 -c "from apgi.protocols import verify_lock; verify_lock()"
case "${1:-}" in
  --upgrade) ots upgrade protocols/MANIFEST.json.ots ;;
  --verify)  ots verify protocols/MANIFEST.json.ots ;;
  *)         ots stamp protocols/MANIFEST.json ;;
esac
