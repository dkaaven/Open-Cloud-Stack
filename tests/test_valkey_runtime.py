import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules" / "data" / "valkey"
NETWORK = ROOT / "modules" / "core" / "network" / "quadlet"

MANIFEST = MODULE / "module.yaml"
CONFIG = MODULE / "config" / "valkey.conf"
START = MODULE / "config" / "start.sh"
HEALTHCHECK = MODULE / "config" / "healthcheck.sh"
HOST_CHECK = MODULE / "health" / "check-host.sh"

CONTAINER = MODULE / "quadlet" / "cloudstack-data-valkey.container"
VOLUME = MODULE / "quadlet" / "cloudstack-data-valkey-data.volume"

GENERATOR = Path("/usr/lib/systemd/system-generators/podman-system-generator")

IMAGE = "docker.io/valkey/valkey@sha256:ee91f7a174ac4d6a6b0685b3a60e321f0a9dbbb691f9b0e285be2ba1d1be8328"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict)
    return data


def test_valkey_manifest_contract():
    module = load_yaml(MANIFEST)

    assert module["stateful"] is True
    assert module["requires"] == ["core/network"]
    assert module["provides"] == ["cache"]
    assert module["secrets"] == ["valkey-password"]
    assert module["networks"] == ["data"]
    assert module["storage"] == [{"id": "data", "backup": False}]
    assert module["images"] == [
        {
            "id": "valkey",
            "version": "9.1.1-alpine",
            "reference": IMAGE,
        }
    ]


def test_valkey_configuration_contract():
    lines = set(
        line.strip()
        for line in CONFIG.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )

    assert "bind 0.0.0.0" in lines
    assert "protected-mode yes" in lines
    assert "port 6379" in lines
    assert "dir /data" in lines
    assert "appendonly yes" in lines
    assert "appendfsync everysec" in lines
    assert "aclfile /tmp/cloudstack-valkey-users.acl" in lines


def test_valkey_startup_uses_secret_without_command_line_password():
    content = START.read_text(encoding="utf-8")

    assert "/run/secrets/valkey-password" in content
    assert 'password="$(cat "${secret}")"' in content
    assert "Valkey password must be hexadecimal." in content
    assert "at least 64 hexadecimal characters" in content
    assert "user default on >%s ~* +@all" in content
    assert "exec valkey-server /etc/valkey/valkey.conf" in content
    assert "--requirepass" not in content


def test_valkey_healthcheck_authenticates():
    content = HEALTHCHECK.read_text(encoding="utf-8")

    assert "/run/secrets/valkey-password" in content
    assert "valkey-cli" in content
    assert "--no-auth-warning" in content
    assert '-a "${password}"' in content
    assert '"PONG"' in content


def test_valkey_quadlet_contract():
    content = CONTAINER.read_text(encoding="utf-8")
    lines = set(content.splitlines())

    assert f"Image={IMAGE}" in lines
    assert "ContainerName=cloudstack-data-valkey" in lines
    assert "Network=cloudstack-data.network" in lines
    assert "Volume=cloudstack-data-valkey-data.volume:/data" in lines
    assert "Volume=/etc/cloudstack/modules/data/valkey/config:/etc/valkey:ro" in lines
    assert "Secret=valkey-password,target=valkey-password" in lines
    assert "User=999" in lines
    assert "Group=1000" in lines
    assert "Exec=/etc/valkey/start.sh" in lines
    assert "HealthCmd=/etc/valkey/healthcheck.sh" in lines
    assert "NoNewPrivileges=true" in lines
    assert "ReadOnly=true" in lines
    assert "DropCapability=ALL" in lines
    assert not any(line.startswith("AddCapability=") for line in lines)
    assert not any(line.startswith("PublishPort=") for line in lines)


def test_valkey_volume_contract():
    lines = set(VOLUME.read_text(encoding="utf-8").splitlines())

    assert "VolumeName=cloudstack-data-valkey-data" in lines
    assert "Label=io.cloudstack.module=data/valkey" in lines
    assert "Label=io.cloudstack.storage=data" in lines
    assert "User=999" in lines
    assert "Group=1000" in lines


def test_valkey_scripts_are_executable():
    assert os.access(START, os.X_OK)
    assert os.access(HEALTHCHECK, os.X_OK)
    assert os.access(HOST_CHECK, os.X_OK)


def test_valkey_quadlet_generates_systemd_units(tmp_path: Path):
    if not GENERATOR.is_file():
        pytest.skip("Podman Quadlet systemd generator is not installed")

    for source in (
        NETWORK / "cloudstack-data.network",
        VOLUME,
        CONTAINER,
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
    assert "cloudstack-data-network.service" in output
    assert "cloudstack-data-valkey-data-volume.service" in output
    assert "cloudstack-data-valkey.service" in output
    assert IMAGE in output
    assert "--network cloudstack-data" in output
    assert "--user 999:1000" in output
    assert "--read-only" in output
    assert "--cap-drop all" in output
    assert "valkey-password,target=valkey-password" in output
    assert "--publish" not in output
