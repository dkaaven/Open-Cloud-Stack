from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "runtime" / "install-stack.sh"
VALKEY_CHECK = (
    ROOT
    / "modules"
    / "data"
    / "valkey"
    / "health"
    / "check-host.sh"
)
PROXMOX_DOC = ROOT / "docs" / "platforms" / "proxmox-lxc.md"


def test_installer_supports_module_host_preflight():
    content = INSTALLER.read_text(encoding="utf-8")

    assert "check_module_host_requirements()" in content
    assert 'modules/${module_id}/health/check-host.sh' in content
    assert '[[ -f "${check}" ]] || continue' in content
    assert '[[ -x "${check}" ]]' in content
    assert '"${check}" ||' in content


def test_host_preflight_happens_before_secret_and_stack_changes():
    content = INSTALLER.read_text(encoding="utf-8")
    main = content[content.index("main() {"):]

    host_check = main.index(
        'check_module_host_requirements "${modules[@]}"'
    )
    secret_check = main.index("check_required_secrets")
    stack_stop = main.index("systemctl stop cloudstack.target")

    assert host_check < secret_check < stack_stop


def test_failed_host_preflight_is_declared_non_destructive():
    content = INSTALLER.read_text(encoding="utf-8")

    assert (
        "Host requirement check failed for module: ${module_id}. "
        "No changes were made."
    ) in content


def test_valkey_host_check_enforces_memory_overcommit():
    content = VALKEY_CHECK.read_text(encoding="utf-8")

    assert "vm.overcommit_memory" in content
    assert '[[ "${value}" == "1" ]]' in content
    assert "exit 1" in content


def test_proxmox_docs_include_cloudstack_lxc_requirements():
    content = PROXMOX_DOC.read_text(encoding="utf-8")

    assert "unprivileged=1" in content
    assert "features=nesting=1,keyctl=1" in content
    assert "vm.overcommit_memory=1" in content
    assert "/etc/sysctl.d/99-cloudstack-valkey.conf" in content
    assert "Proxmox host" in content
