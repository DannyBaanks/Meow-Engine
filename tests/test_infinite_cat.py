# tests/test_infinite_cat.py
"""El experimento del gatito infinito: el gato se construye, no se elige."""
import json
from pathlib import Path

import generate_cat as gc

CANONICAL = " /\\_/\\\n( o.o )\n > ^ <"  # el MISMO gato del harness


def test_canonical_cat_emerges_only_from_all_zero_bytes():
    cat, hits, verdict = gc.build_cat([0] * 8)
    assert cat == CANONICAL
    assert hits == 8
    assert verdict == "CAT"


def test_basins():
    assert gc.build_cat([0, 0, 0, 0, 0, 0, 0, 5])[2] == "DOG"          # 7 hits
    assert gc.build_cat([1] * 8)[2] == "CUP"                           # 0 hits
    assert gc.build_cat([0] * 3 + [1, 2, 3, 4, 5])[2] == "ABOMINATION"  # 3 hits


def test_no_abomination_equals_canonical_piece():
    # si un byte distinto de cero pudiera producir la pieza canónica,
    # la prueba "8 hits == gato real" se rompería. Los pools no la contienen.
    for name, canonical, pool in gc.PARTS:
        assert canonical not in pool, name
        for b in range(1, 256):
            assert pool[b % len(pool)] != canonical


def test_probability_is_honest():
    # P(CAT) = (1/256)^8 = 2^-64; una sola parte distinta NO basta
    assert len(gc.PARTS) == 8
    _, hits, verdict = gc.build_cat([0] * 7 + [0])  # == 8
    assert verdict == "CAT"
    _, hits, verdict = gc.build_cat([0] * 6 + [0, 0])  # idem
    assert hits == 8


def test_main_writes_cat_and_audit_log(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    gc.LOG_PATH = str(tmp_path / "cat_log.jsonl")
    gc.main()
    cat_txt = (tmp_path / "cat.txt").read_text(encoding="utf-8")
    assert cat_txt
    lines = gc.LOG_PATH and Path(gc.LOG_PATH).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["entropy_source"].startswith("secrets.randbits(64)")
    assert len(rec["roll_hex"]) == 16
    assert len(rec["bytes"]) == 8
    assert rec["verdict"] in gc.VERDICTS
    assert rec["cat"] == cat_txt
    # regla sagrada: el log no contiene fecha-decisión ni contador
    assert "day" not in rec and "counter" not in rec
