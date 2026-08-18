import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"
PROFILES = ROOT / "profiles"

MODULE_SCHEMA = json.loads(
    (ROOT / "schemas" / "module.schema.json").read_text(encoding="utf-8")
)
PROFILE_SCHEMA = json.loads(
    (ROOT / "schemas" / "profile.schema.json").read_text(encoding="utf-8")
)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def module_dirs() -> list[Path]:
    if not MODULES.exists():
        return []

    return sorted(
        path
        for category in MODULES.iterdir()
        if category.is_dir() and not category.name.startswith(".")
        for path in category.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def module_files() -> list[Path]:
    return [path / "module.yaml" for path in module_dirs()]


def profile_files() -> list[Path]:
    if not PROFILES.exists():
        return []
    return sorted(PROFILES.glob("*.yaml"))


def modules_by_id() -> dict[str, dict]:
    modules = {}
    for manifest in module_files():
        if not manifest.is_file():
            continue
        data = load_yaml(manifest)
        modules[data["id"]] = data
    return modules


def dependency_closure(module_id: str, modules: dict[str, dict]) -> set[str]:
    found: set[str] = set()
    pending = list(modules[module_id]["requires"])

    while pending:
        dependency = pending.pop()
        if dependency in found:
            continue
        found.add(dependency)
        if dependency in modules:
            pending.extend(modules[dependency]["requires"])

    return found


def test_module_schema_is_valid():
    Draft202012Validator.check_schema(MODULE_SCHEMA)


def test_profile_schema_is_valid():
    Draft202012Validator.check_schema(PROFILE_SCHEMA)


def test_repository_contains_modules():
    assert module_dirs(), "No module directories found"


def test_all_module_directories_have_required_files():
    missing = []

    for module in module_dirs():
        for required in ("module.yaml", "README.md"):
            if not (module / required).is_file():
                missing.append(str((module / required).relative_to(ROOT)))

    assert not missing, "Missing required module files:\n" + "\n".join(missing)


@pytest.mark.parametrize("manifest", module_files())
def test_module_manifest_valid(manifest: Path):
    if not manifest.is_file():
        pytest.skip("reported by required-files test")

    Draft202012Validator(MODULE_SCHEMA).validate(load_yaml(manifest))


@pytest.mark.parametrize("manifest", module_files())
def test_module_id_matches_path(manifest: Path):
    if not manifest.is_file():
        pytest.skip("reported by required-files test")

    data = load_yaml(manifest)
    expected = "/".join(manifest.relative_to(MODULES).parts[:2])
    assert data["id"] == expected


def test_module_dependencies_exist():
    modules = modules_by_id()
    missing = []

    for module_id, data in modules.items():
        for dependency in data["requires"]:
            if dependency not in modules:
                missing.append(f"{module_id} -> {dependency}")

    assert not missing, "Missing module dependencies:\n" + "\n".join(missing)


def test_module_does_not_depend_on_itself():
    modules = modules_by_id()

    for module_id, data in modules.items():
        assert module_id not in data["requires"], f"{module_id} depends on itself"


def test_profiles_directory_contains_only_yaml_files():
    if not PROFILES.exists():
        pytest.fail("profiles/ does not exist")

    invalid = sorted(
        str(path.relative_to(ROOT))
        for path in PROFILES.iterdir()
        if not path.name.startswith(".") and not (path.is_file() and path.suffix == ".yaml")
    )

    assert not invalid, "Profiles must be flat YAML files:\n" + "\n".join(invalid)


def test_repository_contains_profiles():
    assert profile_files(), "No profile manifests found"


@pytest.mark.parametrize("profile", profile_files())
def test_profile_manifest_valid(profile: Path):
    Draft202012Validator(PROFILE_SCHEMA).validate(load_yaml(profile))


@pytest.mark.parametrize("profile", profile_files())
def test_profile_id_matches_filename(profile: Path):
    assert load_yaml(profile)["id"] == profile.stem


def test_profile_modules_exist():
    modules = modules_by_id()
    missing = []

    for profile in profile_files():
        data = load_yaml(profile)
        for module_id in data["modules"]:
            if module_id not in modules:
                missing.append(f"{profile.name} -> {module_id}")

    assert not missing, "Profiles reference missing modules:\n" + "\n".join(missing)


def test_profiles_do_not_duplicate_dependencies():
    modules = modules_by_id()
    redundant = []

    for profile in profile_files():
        selected = set(load_yaml(profile)["modules"])

        for module_id in selected:
            if module_id not in modules:
                continue
            duplicated = selected & dependency_closure(module_id, modules)
            for dependency in sorted(duplicated):
                redundant.append(f"{profile.name}: {dependency} is already required by {module_id}")

    assert not redundant, "Profiles contain transitive dependencies:\n" + "\n".join(redundant)
