from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "runtime" / "install-stack.sh"


def test_installer_supports_module_configuration_hooks():
    content = INSTALLER.read_text(encoding="utf-8")

    assert "run_module_configure()" in content
    assert "check_module_configuration()" in content
    assert "configure_modules()" in content
    assert 'modules/${module_id}/configure.sh' in content


def test_configuration_preflight_is_non_destructive():
    content = INSTALLER.read_text(encoding="utf-8")
    main = content[content.index("main() {"):]

    configuration = main.index(
        'check_module_configuration "${modules[@]}"'
    )
    secrets = main.index("check_required_secrets")
    stop = main.index("systemctl stop cloudstack.target")

    assert configuration < secrets < stop


def test_module_configuration_is_applied_before_secrets_and_reload():
    content = INSTALLER.read_text(encoding="utf-8")
    main = content[content.index("main() {"):]

    configure = main.index('configure_modules "${modules[@]}"')
    secrets = main.index("prepare_secrets")
    reload = main.index("systemctl daemon-reload")

    assert configure < secrets < reload
