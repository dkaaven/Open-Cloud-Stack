from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
MODULES = ROOT / "modules"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def module_files() -> list[Path]:
    return sorted(MODULES.glob("*/*/module.yaml"))


def test_configuration_examples_exist():
    assert (CONFIG / "stack.env.example").is_file()
    assert (CONFIG / "customer.env.example").is_file()


def test_deployment_env_files_are_not_in_source():
    forbidden = sorted(
        str(path.relative_to(ROOT))
        for path in CONFIG.glob("*.env")
        if path.is_file()
    )

    assert not forbidden, "Deployment configuration must not be committed:\n" + "\n".join(forbidden)


def test_repository_contains_no_secret_directories():
    forbidden = sorted(
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("secrets")
        if path.is_dir() and ".venv" not in path.parts
    )

    assert not forbidden, "Secret directories must not exist in source:\n" + "\n".join(forbidden)


def test_declared_secret_ids_are_module_scoped():
    invalid = []

    for manifest in module_files():
        data = load_yaml(manifest)
        module_name = data["id"].split("/", 1)[1]

        for secret_id in data.get("secrets", []):
            if not secret_id.startswith(f"{module_name}-"):
                invalid.append(f"{data['id']}: {secret_id}")

    assert not invalid, (
        "Secret identifiers must start with the module name:\n" + "\n".join(invalid)
    )
