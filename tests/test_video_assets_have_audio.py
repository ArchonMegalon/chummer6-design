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


def test_all_video_links_include_aac_audio_note() -> None:
    missing: list[str] = []

    for path, lineno, line, _url in video_check._iter_video_lines():
        if "MP4 with AAC audio" not in line:
            missing.append(f"{path}:{lineno}")

    assert not missing, f"video links missing explicit audio note: {', '.join(missing)}"
