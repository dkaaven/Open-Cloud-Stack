from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"

SHARED_NETWORK_QUADLETS = {
    "cloudstack-edge.network",
    "cloudstack-data.network",
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def module_files() -> list[Path]:
    return sorted(MODULES.glob("*/*/module.yaml"))


def test_image_ids_are_unique_per_module():
    failures = []

    for manifest in module_files():
        module = load_yaml(manifest)
        ids = [image["id"] for image in module["images"]]

        if len(ids) != len(set(ids)):
            failures.append(module["id"])

    assert not failures, "Duplicate image IDs:\n" + "\n".join(failures)


def test_latest_is_not_used_as_image_version():
    failures = []

    for manifest in module_files():
        module = load_yaml(manifest)

        for image in module["images"]:
            if image["version"].lower() == "latest":
                failures.append(f"{module['id']}: {image['id']}")

    assert not failures, "`latest` image versions are not allowed:\n" + "\n".join(failures)


def test_image_references_are_digest_pinned():
    failures = []

    for manifest in module_files():
        module = load_yaml(manifest)

        for image in module["images"]:
            reference = image["reference"]

            if "@sha256:" not in reference:
                failures.append(f"{module['id']}: {reference}")

    assert not failures, "Images must use digest references:\n" + "\n".join(failures)


def test_quadlet_resource_names_follow_module_id():
    failures = []

    for module_dir in sorted(path for path in MODULES.glob("*/*") if path.is_dir()):
        quadlet_dir = module_dir / "quadlet"

        if not quadlet_dir.is_dir():
            continue

        category = module_dir.parent.name
        module = module_dir.name
        prefix = f"cloudstack-{category}-{module}"

        for resource in sorted(path for path in quadlet_dir.iterdir() if path.is_file()):
            if (
                category == "core"
                and module == "network"
                and resource.name in SHARED_NETWORK_QUADLETS
            ):
                continue

            if not (
                resource.stem == prefix
                or resource.stem.startswith(prefix + "-")
            ):
                failures.append(str(resource.relative_to(ROOT)))

    assert not failures, (
        "Quadlet resource names must follow the module namespace:\n"
        + "\n".join(failures)
    )
