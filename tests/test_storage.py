from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def module_files() -> list[Path]:
    return sorted(MODULES.glob("*/*/module.yaml"))


def test_stateful_modules_declare_storage():
    failures = []

    for manifest in module_files():
        module = load_yaml(manifest)
        if module["stateful"] and not module["storage"]:
            failures.append(module["id"])

    assert not failures, "Stateful modules without storage:\n" + "\n".join(failures)


def test_stateless_modules_do_not_declare_storage():
    failures = []

    for manifest in module_files():
        module = load_yaml(manifest)
        if not module["stateful"] and module["storage"]:
            failures.append(module["id"])

    assert not failures, "Stateless modules with storage:\n" + "\n".join(failures)


def test_storage_ids_are_unique_per_module():
    failures = []

    for manifest in module_files():
        module = load_yaml(manifest)
        ids = [entry["id"] for entry in module["storage"]]

        if len(ids) != len(set(ids)):
            failures.append(module["id"])

    assert not failures, "Duplicate storage IDs:\n" + "\n".join(failures)


def test_backup_storage_has_backup_directory():
    failures = []

    for manifest in module_files():
        module = load_yaml(manifest)

        if any(entry["backup"] for entry in module["storage"]):
            if not (manifest.parent / "backup").is_dir():
                failures.append(module["id"])

    assert not failures, (
        "Modules with backup-required storage must have backup/:\n"
        + "\n".join(failures)
    )


def test_network_module_is_stateless():
    module = load_yaml(MODULES / "core" / "network" / "module.yaml")

    assert module["stateful"] is False
    assert module["storage"] == []


def test_postgres_data_requires_backup():
    module = load_yaml(MODULES / "data" / "postgres" / "module.yaml")

    assert module["storage"] == [{"id": "data", "backup": True}]


def test_valkey_data_is_disposable():
    module = load_yaml(MODULES / "data" / "valkey" / "module.yaml")

    assert module["storage"] == [{"id": "data", "backup": False}]


def test_nextcloud_data_requires_backup():
    module = load_yaml(MODULES / "workplace" / "nextcloud" / "module.yaml")

    assert module["storage"] == [{"id": "data", "backup": True}]
