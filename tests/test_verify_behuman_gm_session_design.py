from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path("/docker/chummercomplete/chummer-design")


def test_behuman_gm_session_design_validator_passes() -> None:
    result = subprocess.run(
        ["python3", str(ROOT / "scripts" / "ai" / "verify_behuman_gm_session_design.py")],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "BEHUMAN_GM_SESSION_DESIGN_OK" in result.stdout
