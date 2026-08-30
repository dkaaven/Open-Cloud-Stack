import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOLVER = ROOT / "runtime" / "lib" / "resolve.py"


def resolve(*extra: str) -> list[str]:
    result = subprocess.run(
        [
            "python3",
            str(RESOLVER),
            "--repo",
            str(ROOT),
            "--profile",
            "workplace",
            *extra,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    return [line for line in result.stdout.splitlines() if line]


def test_workplace_profile_resolves_nextcloud_secrets():
    assert resolve("--secrets") == [
        "postgres-superuser-password",
        "valkey-password",
        "nextcloud-db-password",
        "nextcloud-admin-password",
    ]
