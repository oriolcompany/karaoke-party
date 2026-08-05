"""Stem path resolution must not trust cwd-relative Demucs basenames."""

from __future__ import annotations

from pathlib import Path

from karaoke_party.stems import _classify, _resolve_outputs, _safe_input_copy


def test_resolve_outputs_prefers_scratch_over_cwd(tmp_path: Path, monkeypatch) -> None:
    scratch = tmp_path / "stems-work"
    scratch.mkdir()
    real = scratch / "kp_vocals.flac"
    real.write_bytes(b"vocal-bytes")

    cwd = tmp_path / "cwd"
    cwd.mkdir()
    ghost = cwd / "kp_vocals.flac"
    ghost.write_bytes(b"wrong")
    monkeypatch.chdir(cwd)

    resolved = _resolve_outputs(["kp_vocals.flac"], scratch)
    assert resolved == [real.resolve()]


def test_resolve_outputs_ignores_missing_basenames(tmp_path: Path) -> None:
    scratch = tmp_path / "stems-work"
    scratch.mkdir()
    assert _resolve_outputs(["missing.flac"], scratch) == []


def test_resolve_outputs_skips_input_copy_on_fallback(tmp_path: Path) -> None:
    scratch = tmp_path / "stems-work"
    scratch.mkdir()
    (scratch / "kp-input.mp3").write_bytes(b"source")
    stem = scratch / "kp_drums.flac"
    stem.write_bytes(b"drum")
    resolved = _resolve_outputs([], scratch)
    assert resolved == [stem.resolve()]


def test_classify_recognizes_stable_output_names(tmp_path: Path) -> None:
    vocals = tmp_path / "kp_vocals.flac"
    drums = tmp_path / "kp_drums.flac"
    instrumental = tmp_path / "kp_instrumental.flac"
    for path in (vocals, drums, instrumental):
        path.write_bytes(b"x")
    v, inst, others = _classify([vocals, drums, instrumental])
    assert v == [vocals]
    assert inst == [instrumental]
    assert others == [drums]


def test_safe_input_copy_uses_plain_ascii_name(tmp_path: Path) -> None:
    music = tmp_path / "La Ludwig Band - El teu amor (àudio oficial) [cspHYorxTdw].mp3"
    music.write_bytes(b"ID3fake")
    scratch = tmp_path / "stems-work"
    scratch.mkdir()
    copied = _safe_input_copy(music, scratch)
    assert copied.name == "kp-input.mp3"
    assert copied.read_bytes() == b"ID3fake"
