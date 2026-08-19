import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "runtime" / "install-podman.sh"


def test_install_podman_script_is_valid_bash():
    result = subprocess.run(
        ["bash", "-n", str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_install_podman_requires_debian_13():
    content = SCRIPT.read_text(encoding="utf-8")

    assert 'ID:-}" == "debian"' in content
    assert 'VERSION_ID:-}" == "13"' in content


def test_install_podman_uses_rootful_layout():
    content = SCRIPT.read_text(encoding="utf-8")

    assert '"/etc/containers/systemd"' in content
    assert '"/etc/cloudstack"' in content
    assert '"/var/lib/cloudstack"' in content


def test_install_podman_checks_quadlet_and_cgroup_v2():
    content = SCRIPT.read_text(encoding="utf-8")

    assert "podman-system-generator" in content
    assert "CgroupsVersion" in content
    assert '"v2"' in content


def test_install_podman_tests_nested_resources():
    content = SCRIPT.read_text(encoding="utf-8")

    assert "podman network create cloudstack-install-test" in content
    assert "podman volume create cloudstack-install-test" in content


def test_installer_installs_aardvark_dns():
    installer = ROOT / "runtime" / "install-podman.sh"
    content = installer.read_text(encoding="utf-8")

    assert "aardvark-dns" in content
