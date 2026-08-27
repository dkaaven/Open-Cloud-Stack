import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "platform.yaml"
RESOLVER = ROOT / "runtime" / "lib" / "resolve.py"


def run_resolver(*extra: str) -> list[str]:
    result = subprocess.run(
        [
            "python3",
            str(RESOLVER),
            "--repo",
            str(ROOT),
            "--profile",
            "platform",
            *extra,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    return [line for line in result.stdout.splitlines() if line]


def test_platform_profile_selects_shared_platform_services():
    with PROFILE.open(encoding="utf-8") as file:
        profile = yaml.safe_load(file)

    assert profile == {
        "schema": 1,
        "id": "platform",
        "modules": [
            "core/traefik",
            "data/postgres",
            "data/valkey",
        ],
    }


def test_platform_profile_resolves_dependency_order():
    assert run_resolver() == [
        "core/network",
        "core/traefik",
        "data/postgres",
        "data/valkey",
    ]


def test_platform_profile_resolves_required_secrets():
    assert run_resolver("--secrets") == [
        "postgres-superuser-password",
        "valkey-password",
    ]
