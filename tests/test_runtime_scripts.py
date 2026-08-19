import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"


@pytest.mark.parametrize("script", sorted(RUNTIME.glob("*.sh")))
def test_runtime_script_is_valid_bash(script: Path):
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"{script.name}: {result.stderr}"