import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOLVER = ROOT / "runtime" / "lib" / "resolve.py"


def resolve(profile: str, *extra: str) -> list[str]:
    result = subprocess.run(
        [
            "python3",
            str(RESOLVER),
            "--repo",
            str(ROOT),
            "--profile",
            profile,
            *extra,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    return [line for line in result.stdout.splitlines() if line]


def test_core_profile_resolves_dependencies_first():
    assert resolve("core") == [
        "core/network",
        "core/traefik",
    ]


def test_workplace_profile_resolves_full_dependency_graph():
    modules = resolve("workplace")

    assert set(modules) == {
        "core/network",
        "core/traefik",
        "data/postgres",
        "data/valkey",
        "workplace/nextcloud",
    }

    assert modules.index("core/network") < modules.index("core/traefik")
    assert modules.index("core/traefik") < modules.index("workplace/nextcloud")
    assert modules.index("data/postgres") < modules.index("workplace/nextcloud")
    assert modules.index("data/valkey") < modules.index("workplace/nextcloud")


def test_workplace_profile_resolves_required_secrets():
    assert resolve("workplace", "--secrets") == [
        "postgres-superuser-password",
    ]


def test_missing_profile_fails_cleanly():
    result = subprocess.run(
        [
            "python3",
            str(RESOLVER),
            "--repo",
            str(ROOT),
            "--profile",
            "does-not-exist",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "ERROR" in result.stderr
