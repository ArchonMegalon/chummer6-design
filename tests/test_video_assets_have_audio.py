from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(
    "/docker/chummercomplete/chummer-design/scripts/ai/verify_video_assets_have_audio.py"
)
SPEC = importlib.util.spec_from_file_location("verify_video_assets_have_audio", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
video_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(video_check)


def test_video_links_do_not_expose_codec_or_caption_plumbing() -> None:
    leaks: list[str] = []

    for path, lineno, line, _url in video_check._iter_video_lines():
        if "MP4 with AAC audio" in line or "Captions are at" in line:
            leaks.append(f"{path}:{lineno}")

    assert not leaks, f"video links expose technical plumbing: {', '.join(leaks)}"


def test_silent_audio_signal_is_a_publication_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        video_check,
        "_probe_media",
        lambda _target: {
            "streams": [
                {"codec_type": "video", "codec_name": "h264"},
                {"codec_type": "audio", "codec_name": "aac", "bit_rate": "2275"},
            ]
        },
    )
    monkeypatch.setattr(
        video_check,
        "_measure_volume",
        lambda _target: {"mean_volume_db": -91.0, "max_volume_db": -91.0},
    )

    failures = video_check._audit_media_target("https://chummer.run/media/horizons/alice-90s-deepdive.mp4")

    assert any(item.startswith("silent_or_placeholder_audio:") for item in failures)
    assert any(item.startswith("placeholder_aac_bitrate:") for item in failures)


def test_non_silent_audio_signal_passes(monkeypatch) -> None:
    monkeypatch.setattr(
        video_check,
        "_probe_media",
        lambda _target: {
            "streams": [
                {"codec_type": "video", "codec_name": "h264"},
                {"codec_type": "audio", "codec_name": "aac", "bit_rate": "169194"},
            ]
        },
    )
    monkeypatch.setattr(
        video_check,
        "_measure_volume",
        lambda _target: {"mean_volume_db": -19.0, "max_volume_db": -3.8},
    )

    assert video_check._audit_media_target("local-alice.mp4") == []
