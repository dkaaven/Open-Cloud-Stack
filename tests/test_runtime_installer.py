from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

INSTALL = ROOT / "runtime" / "install-stack.sh"
UNINSTALL = ROOT / "runtime" / "uninstall-stack.sh"
BOOTSTRAP = ROOT / "runtime" / "bootstrap.sh"
PODMAN_INSTALL = ROOT / "runtime" / "install-podman.sh"


def test_installer_is_profile_driven():
    content = INSTALL.read_text(encoding="utf-8")

    assert "--profile" in content
    assert "lib/resolve.py" in content
    assert "/etc/cloudstack/runtime" in content
    assert "/etc/containers/systemd/cloudstack" in content
    assert "cloudstack.target" in content


def test_installer_requires_root_instead_of_auto_sudo():
    content = INSTALL.read_text(encoding="utf-8")

    assert '[[ "${EUID}" -eq 0 ]]' in content
    assert "exec sudo" not in content


def test_bootstrap_installs_runtime_then_stack():
    content = BOOTSTRAP.read_text(encoding="utf-8")

    assert 'runtime/install-podman.sh"' in content
    assert 'runtime/install-stack.sh" --profile "${PROFILE}"' in content
    assert 'CLOUDSTACK_PROFILE:-core' in content


def test_podman_installer_provides_yaml_runtime_dependency():
    content = PODMAN_INSTALL.read_text(encoding="utf-8")

    assert "python3-yaml" in content


def test_uninstall_preserves_persistent_data():
    content = UNINSTALL.read_text(encoding="utf-8")

    assert "/var/lib/cloudstack were NOT deleted" in content
    assert "podman volume rm" not in content
