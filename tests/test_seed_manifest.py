"""Consistency of the seed-dataset release record (data/seeds/seed_manifest.json)."""

from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

from apgi.scripts import fetch_data

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "seeds" / "seed_manifest.json"
CHECKSUMS = ROOT / "data" / "checksums.sha256"


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def _checksums() -> dict[str, str]:
    out = {}
    for line in CHECKSUMS.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            digest, name = line.split(maxsplit=1)
            out[name.strip()] = digest
    return out


def test_manifest_release_matches_protocols(manifest):
    assert manifest["release"] == "1.1.0"
    assert manifest["protocol_specification"] == "1.1.0"
    for f in sorted((ROOT / "protocols").glob("protocol_*.json")):
        assert json.loads(f.read_text())["version"] == manifest["protocol_specification"]


def test_manifest_covers_every_registered_dataset(manifest):
    names = [d["name"] for d in manifest["datasets"]]
    assert names == list(fetch_data.DATASETS)


def test_manifest_digests_match_checksums_and_registry(manifest):
    checksums = _checksums()
    for d in manifest["datasets"]:
        assert checksums[d["file"]] == d["sha256"], d["name"]
        assert fetch_data.DATASETS[d["name"]][1] == d["sha256"], d["name"]


def test_manifest_references_existing_files(manifest):
    for d in manifest["datasets"]:
        assert (ROOT / d["protocol"]).is_file(), d["protocol"]
        for consumer in d["consumers"]:
            assert (ROOT / consumer).is_file(), consumer
        assert d["v1_1_alignment"] in {"matches", "differs", "not_applicable"}


def test_manifest_records_current_generator(manifest):
    script = ROOT / manifest["generator"]["script"]
    digest = hashlib.sha256(script.read_bytes()).hexdigest()
    assert manifest["generator"]["sha256"] == digest, (
        "data/generate_seeds.py changed; rerun `python data/generate_seeds.py --manifest`"
    )


def test_manifest_sub_seeds_follow_master_seed(manifest):
    np = pytest.importorskip("numpy")
    master = manifest["generator"]["master_seed"]
    expected = np.random.default_rng(master).integers(0, 2**31, len(manifest["datasets"]))
    assert [d["sub_seed"] for d in manifest["datasets"]] == [int(s) for s in expected]
