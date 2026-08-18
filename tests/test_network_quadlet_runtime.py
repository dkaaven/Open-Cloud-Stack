import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
QUADLETS = ROOT / "modules" / "core" / "network" / "quadlet"
GENERATOR = Path("/usr/lib/systemd/system-generators/podman-system-generator")


def test_network_quadlets_are_not_placeholders():
    for name in ("cloudstack-edge.network", "cloudstack-data.network"):
        path = QUADLETS / name

        assert path.is_file()
        assert path.read_text(encoding="utf-8").strip()


def test_network_quadlets_have_network_sections():
    edge = (QUADLETS / "cloudstack-edge.network").read_text(encoding="utf-8")
    data = (QUADLETS / "cloudstack-data.network").read_text(encoding="utf-8")

    assert "[Network]" in edge
    assert "[Network]" in data


def test_network_quadlets_generate_systemd_units():
    if not GENERATOR.is_file():
        pytest.skip("Podman Quadlet systemd generator is not installed")

    env = os.environ.copy()
    env["QUADLET_UNIT_DIRS"] = str(QUADLETS)

    result = subprocess.run(
        [str(GENERATOR), "--dryrun"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert "cloudstack-edge-network.service" in output
    assert "cloudstack-data-network.service" in output
