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


def test_installer_tracks_resources_separately_from_workloads():
    content = INSTALL.read_text(encoding="utf-8")

    assert 'RESOURCE_MANIFEST="${RUNTIME_ROOT}/resources"' in content
    assert 'WORKLOAD_MANIFEST="${RUNTIME_ROOT}/workloads"' in content

    assert "*.network|*.volume)" in content
    assert '>> "${TMP_RESOURCES}"' in content

    assert "*.container|*.pod)" in content
    assert '>> "${TMP_WORKLOADS}"' in content


def test_installer_reconciles_resources_after_daemon_reload():
    content = INSTALL.read_text(encoding="utf-8")

    daemon_reload = content.index("systemctl daemon-reload")
    validate = content.index("validate_units", daemon_reload)
    reconcile = content.index("reconcile_resources", validate)
    start = content.index("systemctl start cloudstack.target", reconcile)

    assert daemon_reload < validate < reconcile < start


def test_resource_reconciliation_restarts_each_resource():
    content = INSTALL.read_text(encoding="utf-8")

    start = content.index("reconcile_resources()")
    end = content.index("\n}\n\nmain()", start)
    function = content[start:end]

    assert 'systemctl restart "${unit}"' in function
    assert 'systemctl is-active --quiet "${unit}"' in function
    assert "Resource reconciliation failed" in function


def test_no_start_still_reconciles_resources():
    content = INSTALL.read_text(encoding="utf-8")

    reconcile = content.index("reconcile_resources", content.index("systemctl daemon-reload"))
    no_start = content.index("if ${START_STACK}; then", reconcile)

    assert reconcile < no_start
