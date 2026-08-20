from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "runtime" / "install-stack.sh"


def test_secret_preflight_happens_before_stack_stop():
    content = INSTALLER.read_text(encoding="utf-8")

    main = content[content.index("main() {"):]
    preflight = main.index("check_required_secrets")
    stop = main.index("systemctl stop cloudstack.target")

    assert preflight < stop


def test_missing_secrets_fail_without_changes():
    content = INSTALLER.read_text(encoding="utf-8")

    assert "Required secrets are missing. No changes were made." in content


def test_existing_podman_secret_is_refreshed_from_deployment_file():
    content = INSTALLER.read_text(encoding="utf-8")

    start = content.index("prepare_secrets()")
    end = content.index("\n}\n\nstop_installed_workloads()", start)
    function = content[start:end]

    assert 'podman secret inspect "${secret}"' in function
    assert 'podman secret rm "${secret}"' in function
    assert 'podman secret create "${secret}" "${source}"' in function


def test_installer_explicitly_waits_for_workload_stop_before_mutation():
    content = INSTALLER.read_text(encoding="utf-8")

    main = content[content.index("main() {"):]

    stop_workloads = main.index("stop_installed_workloads")
    remove_dropins = main.index("remove_old_workload_dropins")
    remove_quadlets = main.index('rm -rf "${QUADLET_ROOT}"')

    assert stop_workloads < remove_dropins < remove_quadlets
