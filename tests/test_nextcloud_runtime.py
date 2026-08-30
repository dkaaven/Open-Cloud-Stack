import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules" / "workplace" / "nextcloud"
NETWORK = ROOT / "modules" / "core" / "network" / "quadlet"

MANIFEST = MODULE / "module.yaml"
CONTAINER = MODULE / "quadlet" / "cloudstack-workplace-nextcloud.container"
CRON = MODULE / "quadlet" / "cloudstack-workplace-nextcloud-cron.container"
VOLUME = MODULE / "quadlet" / "cloudstack-workplace-nextcloud-data.volume"
CONFIGURE = MODULE / "configure.sh"
HEALTH = MODULE / "config" / "healthcheck.sh"
HOOK = (
    MODULE
    / "config"
    / "hooks"
    / "before-starting"
    / "10-cloudstack.sh"
)
POSTGRES = MODULE / "provision" / "postgres.yaml"

GENERATOR = Path("/usr/lib/systemd/system-generators/podman-system-generator")

IMAGE = "docker.io/library/nextcloud@sha256:8e5f49801db0cf4659b3089ce1917728023bb8cba7f93731f2abbdfe3a18df0a"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict)
    return data


def test_nextcloud_manifest_contract():
    module = load_yaml(MANIFEST)

    assert module["stateful"] is True
    assert module["requires"] == [
        "core/network",
        "core/traefik",
        "data/postgres",
        "data/valkey",
    ]
    assert module["secrets"] == [
        "nextcloud-db-password",
        "nextcloud-admin-password",
    ]
    assert module["networks"] == ["edge", "data"]
    assert module["storage"] == [{"id": "data", "backup": True}]
    assert module["images"] == [
        {
            "id": "nextcloud",
            "version": "34.0.3-apache",
            "reference": IMAGE,
        }
    ]


def test_nextcloud_database_contract():
    contract = load_yaml(POSTGRES)

    assert contract == {
        "schema": 1,
        "database": "nextcloud",
        "role": "nextcloud",
        "password_secret": "nextcloud-db-password",
    }


def test_nextcloud_container_contract():
    lines = set(CONTAINER.read_text(encoding="utf-8").splitlines())

    assert f"Image={IMAGE}" in lines
    assert "ContainerName=cloudstack-workplace-nextcloud" in lines
    assert "Network=cloudstack-edge.network" in lines
    assert "Network=cloudstack-data.network" in lines

    assert (
        "Volume=cloudstack-workplace-nextcloud-data.volume:/var/www/html"
        in lines
    )

    assert (
        "EnvironmentFile=/etc/cloudstack/modules/workplace/nextcloud/"
        "config/runtime.env"
        in lines
    )

    assert "Secret=nextcloud-db-password,target=nextcloud-db-password" in lines
    assert (
        "Secret=nextcloud-admin-password,target=nextcloud-admin-password"
        in lines
    )

    assert "NoNewPrivileges=true" in lines
    assert not any(line.startswith("PublishPort=") for line in lines)


def test_nextcloud_cron_is_non_root_and_internal():
    lines = set(CRON.read_text(encoding="utf-8").splitlines())

    assert f"Image={IMAGE}" in lines
    assert "Network=cloudstack-data.network" in lines
    assert "Network=cloudstack-edge.network" not in lines
    assert "User=33" in lines
    assert "Group=33" in lines
    assert "Exec=/cron.sh" in lines
    assert "ReadOnly=true" in lines
    assert "NoNewPrivileges=true" in lines
    assert "DropCapability=ALL" in lines
    assert not any(line.startswith("PublishPort=") for line in lines)


def test_nextcloud_volume_contract():
    lines = set(VOLUME.read_text(encoding="utf-8").splitlines())

    assert "VolumeName=cloudstack-workplace-nextcloud-data" in lines
    assert "Label=io.cloudstack.module=workplace/nextcloud" in lines
    assert "Label=io.cloudstack.storage=data" in lines


def test_nextcloud_runtime_scripts_are_executable():
    for script in (CONFIGURE, HEALTH, HOOK):
        assert os.access(script, os.X_OK), script


def test_nextcloud_configure_renders_runtime_and_route(tmp_path: Path):
    config_root = tmp_path / "cloudstack"

    customer = config_root / "customer.env"
    customer.parent.mkdir(parents=True)
    customer.write_text(
        "CLOUDSTACK_NEXTCLOUD_HOST=cloud.example.test\n"
        "CLOUDSTACK_NEXTCLOUD_PROTOCOL=https\n"
        "CLOUDSTACK_NEXTCLOUD_ADMIN_USER=cloudadmin\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["CLOUDSTACK_CONFIG_ROOT"] = str(config_root)

    check = subprocess.run(
        [str(CONFIGURE), "--check"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, check.stderr

    apply = subprocess.run(
        [str(CONFIGURE), "--apply"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert apply.returncode == 0, apply.stderr

    runtime_env = (
        config_root
        / "modules"
        / "workplace"
        / "nextcloud"
        / "config"
        / "runtime.env"
    ).read_text(encoding="utf-8")

    route = (
        config_root
        / "modules"
        / "core"
        / "traefik"
        / "config"
        / "dynamic"
        / "nextcloud.yaml"
    ).read_text(encoding="utf-8")

    assert "NEXTCLOUD_TRUSTED_DOMAINS=cloud.example.test" in runtime_env
    assert "OVERWRITEPROTOCOL=https" in runtime_env
    assert "POSTGRES_USER=nextcloud" in runtime_env
    assert "REDIS_HOST=cloudstack-data-valkey" in runtime_env

    assert "Host(`cloud.example.test`)" in route
    assert "http://cloudstack-workplace-nextcloud:80" in route


def test_nextcloud_quadlets_generate(tmp_path: Path):
    if not GENERATOR.is_file():
        pytest.skip("Podman Quadlet systemd generator is not installed")

    sources = [
        NETWORK / "cloudstack-edge.network",
        NETWORK / "cloudstack-data.network",
        VOLUME,
        CONTAINER,
        CRON,
    ]

    for source in sources:
        shutil.copy2(source, tmp_path / source.name)

    # The workload units reference dependency service names. The generator
    # only needs the corresponding Quadlet resources for syntax validation.
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
    assert "cloudstack-workplace-nextcloud.service" in output
    assert "cloudstack-workplace-nextcloud-cron.service" in output
    assert "cloudstack-workplace-nextcloud-data-volume.service" in output
    assert IMAGE in output
    assert "--publish" not in output
