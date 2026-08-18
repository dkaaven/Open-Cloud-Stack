import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules" / "data" / "postgres"
NETWORK = ROOT / "modules" / "core" / "network" / "quadlet"

CONTAINER = MODULE / "quadlet" / "cloudstack-data-postgres.container"
VOLUME = MODULE / "quadlet" / "cloudstack-data-postgres-data.volume"
MANIFEST = MODULE / "module.yaml"

GENERATOR = Path("/usr/lib/systemd/system-generators/podman-system-generator")

IMAGE = "docker.io/library/postgres@sha256:697c180dbf244d3ce4a8f4cbc0156cde840af055c1bf8b76aebe422a4822086f"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict)
    return data


def test_postgres_manifest_runtime_contract():
    module = load_yaml(MANIFEST)

    assert module["stateful"] is True
    assert module["networks"] == ["data"]
    assert module["secrets"] == ["postgres-superuser-password"]
    assert module["storage"] == [{"id": "data", "backup": True}]
    assert module["images"] == [
        {
            "id": "database",
            "version": "18.6-alpine3.23",
            "reference": IMAGE,
        }
    ]


def test_postgres_volume_contract():
    content = VOLUME.read_text(encoding="utf-8")

    assert "VolumeName=cloudstack-data-postgres-data" in content


def test_postgres_container_contract():
    content = CONTAINER.read_text(encoding="utf-8")

    assert f"Image={IMAGE}" in content
    assert "ContainerName=cloudstack-data-postgres" in content

    assert "Network=cloudstack-data.network" in content
    assert "cloudstack-edge.network" not in content
    assert "PublishPort=" not in content

    assert (
        "Volume=cloudstack-data-postgres-data.volume:/var/lib/postgresql"
        in content
    )

    assert (
        "Secret=postgres-superuser-password,target=postgres-superuser-password"
        in content
    )
    assert (
        "Environment=POSTGRES_PASSWORD_FILE="
        "/run/secrets/postgres-superuser-password"
        in content
    )

    assert "Environment=POSTGRES_INITDB_ARGS=--data-checksums" in content
    assert "HealthCmd=pg_isready -U postgres -d postgres" in content
    assert "NoNewPrivileges=true" in content


@pytest.mark.parametrize(
    "script",
    [
        MODULE / "health" / "check.sh",
        MODULE / "backup" / "backup.sh",
        MODULE / "backup" / "restore.sh",
    ],
)
def test_postgres_scripts_are_valid_bash(script: Path):
    result = subprocess.run(
        ["bash", "-n", str(script)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_postgres_backup_uses_logical_cluster_dump():
    content = (MODULE / "backup" / "backup.sh").read_text(encoding="utf-8")

    assert "pg_dumpall --clean --if-exists -U postgres" in content
    assert "sha256sum" in content


def test_postgres_restore_uses_psql_and_analyze():
    content = (MODULE / "backup" / "restore.sh").read_text(encoding="utf-8")

    assert "psql -X -U postgres -d postgres" in content
    assert "vacuumdb -U postgres --all --analyze" in content


def test_postgres_quadlets_generate_systemd_units(tmp_path: Path):
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
    assert "cloudstack-data-postgres.service" in output
    assert "cloudstack-data-postgres-data-volume.service" in output
    assert "cloudstack-data-network.service" in output

    assert IMAGE in output
    assert "--network cloudstack-data" in output
    assert "cloudstack-data-postgres-data:/var/lib/postgresql" in output
    assert "--secret postgres-superuser-password" in output
    assert "--health-cmd" in output
