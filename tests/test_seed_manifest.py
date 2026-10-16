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


def test_manifest_records_content_fingerprints(manifest):
    for d in manifest["datasets"]:
        assert d["content"], d["name"]
        for key, entry in d["content"].items():
            assert entry["kind"] in {"f", "i", "u", "b", "U", "S", "O"}, (d["name"], key)
            assert ("sum" in entry) == (entry["kind"] == "f"), (d["name"], key)


@pytest.fixture(scope="module")
def generate_seeds():
    import importlib
    import sys

    sys.path.insert(0, str(ROOT))
    return importlib.import_module("data.generate_seeds")


def _write(path, **arrays):
    np = pytest.importorskip("numpy")
    np.savez_compressed(path, **arrays)
    return path


def test_content_fingerprint_ignores_compression_and_last_bit_noise(tmp_path, generate_seeds):
    import zipfile

    np = pytest.importorskip("numpy")
    rng = np.random.default_rng(0)
    x = rng.normal(size=5_000)
    labels = np.array(["a", "b"] * 10)
    ref = _write(tmp_path / "ref.npz", x=x, flag=x > 0, labels=labels, n=np.array(7))
    noisy = _write(
        tmp_path / "noisy.npz",
        x=np.nextafter(x, np.inf),  # every value moved by one ULP
        flag=x > 0,
        labels=labels,
        n=np.array(7),
        allow_pickle=np.array(True),  # stray key from old generator versions
    )
    # Same arrays, different compression level: different file bytes.
    recompressed = tmp_path / "recompressed.npz"
    with zipfile.ZipFile(ref) as src, zipfile.ZipFile(
        recompressed, "w", zipfile.ZIP_DEFLATED, compresslevel=1
    ) as dst:
        for info in src.infolist():
            dst.writestr(info.filename, src.read(info.filename))

    fp = generate_seeds._content_fingerprint
    diff = generate_seeds._content_differences
    assert ref.read_bytes() != recompressed.read_bytes()
    assert diff(fp(ref), fp(recompressed)) == []
    assert diff(fp(ref), fp(noisy)) == []


def test_content_fingerprint_detects_real_changes(tmp_path, generate_seeds):
    np = pytest.importorskip("numpy")
    x = np.random.default_rng(0).normal(size=1_000)
    ref = _write(tmp_path / "ref.npz", x=x, n=np.array(7))
    fp = generate_seeds._content_fingerprint
    diff = generate_seeds._content_differences
    shifted = x.copy()
    shifted[0] += 1e-6
    assert diff(fp(ref), fp(_write(tmp_path / "a.npz", x=shifted, n=np.array(7)))) == ["x"]
    assert diff(fp(ref), fp(_write(tmp_path / "b.npz", x=x, n=np.array(8)))) == ["n"]
    assert diff(fp(ref), fp(_write(tmp_path / "c.npz", x=x[:-1], n=np.array(7)))) == ["x"]
    assert diff(fp(ref), fp(_write(tmp_path / "d.npz", x=x))) == ["n"]
