import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules" / "core" / "traefik"
NETWORK = ROOT / "modules" / "core" / "network" / "quadlet"
QUADLET = MODULE / "quadlet" / "cloudstack-core-traefik.container"
CONFIG = MODULE / "config" / "traefik.yaml"
MANIFEST = MODULE / "module.yaml"
GENERATOR = Path("/usr/lib/systemd/system-generators/podman-system-generator")

IMAGE = "docker.io/library/traefik@sha256:9c3b91d5fb7770853ca5c1124a23c34bf2d9b47ffaebeab2614cbaf410dcb2ac"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict)
    return data


def test_traefik_manifest_runtime_contract():
    module = load_yaml(MANIFEST)

    assert module["stateful"] is False
    assert module["storage"] == []
    assert module["networks"] == ["edge"]
    assert module["images"] == [
        {
            "id": "proxy",
            "version": "3.7.10",
            "reference": IMAGE,
        }
    ]


def test_traefik_static_configuration():
    config = load_yaml(CONFIG)

    assert config["entryPoints"]["web"]["address"] == ":80"
    assert config["entryPoints"]["websecure"]["address"] == ":443"
    assert config["entryPoints"]["health"]["address"] == ":8080"

    assert config["providers"]["file"]["directory"] == "/etc/traefik/dynamic"
    assert config["providers"]["file"]["watch"] is True
    assert "docker" not in config["providers"]

    assert config["ping"]["entryPoint"] == "health"


def test_traefik_quadlet_contract():
    content = QUADLET.read_text(encoding="utf-8")

    assert f"Image={IMAGE}" in content
    assert "ContainerName=cloudstack-core-traefik" in content
    assert "Network=cloudstack-edge.network" in content
    assert "PublishPort=80:80" in content
    assert "PublishPort=443:443" in content
    assert "Volume=/etc/cloudstack/traefik:/etc/traefik:ro" in content
    assert "HealthCmd=traefik healthcheck" in content
    assert "NoNewPrivileges=true" in content
    assert "ReadOnly=true" in content

    assert "podman.sock" not in content
    assert "docker.sock" not in content


def test_traefik_quadlet_generates_systemd_unit(tmp_path: Path):
    if not GENERATOR.is_file():
        pytest.skip("Podman Quadlet systemd generator is not installed")

    for source in (
        NETWORK / "cloudstack-edge.network",
        QUADLET,
    ):
        shutil.copy2(source, tmp_path / source.name)

    env = os.environ.copy()
    env["QUADLET_UNIT_DIRS"] = str(tmp_path.resolve())

    result = subprocess.run(
        [str(GENERATOR), "--dryrun"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    assert "cloudstack-core-traefik.service" in output
    assert "cloudstack-edge-network.service" in output
    assert IMAGE in output
    assert "--network cloudstack-edge" in output
    assert "--publish 80:80" in output
    assert "--publish 443:443" in output
