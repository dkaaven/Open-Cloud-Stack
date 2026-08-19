#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


class ResolveError(Exception):
    pass


def load_yaml(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError as exc:
        raise ResolveError(f"File not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ResolveError(f"Invalid YAML: {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ResolveError(f"Expected YAML mapping: {path}")

    return data


def discover_modules(repo: Path) -> dict[str, dict]:
    modules: dict[str, dict] = {}

    for manifest in sorted((repo / "modules").glob("*/*/module.yaml")):
        data = load_yaml(manifest)
        module_id = data.get("id")

        if not isinstance(module_id, str) or not module_id:
            raise ResolveError(f"Missing module id: {manifest}")

        if module_id in modules:
            raise ResolveError(f"Duplicate module id: {module_id}")

        data["_path"] = manifest.parent
        modules[module_id] = data

    return modules


def resolve_profile(repo: Path, profile_id: str) -> list[dict]:
    profile = load_yaml(repo / "profiles" / f"{profile_id}.yaml")

    if profile.get("id") != profile_id:
        raise ResolveError(
            f"Profile id mismatch: expected {profile_id}, found {profile.get('id')!r}"
        )

    selected = profile.get("modules")
    if not isinstance(selected, list):
        raise ResolveError(f"Profile {profile_id} has no modules list")

    modules = discover_modules(repo)
    ordered: list[dict] = []
    permanent: set[str] = set()
    temporary: list[str] = []

    def visit(module_id: str) -> None:
        if module_id in permanent:
            return

        if module_id in temporary:
            cycle = " -> ".join([*temporary, module_id])
            raise ResolveError(f"Dependency cycle: {cycle}")

        module = modules.get(module_id)
        if module is None:
            raise ResolveError(f"Missing module dependency: {module_id}")

        temporary.append(module_id)

        requires = module.get("requires", [])
        if not isinstance(requires, list):
            raise ResolveError(f"Invalid requires list: {module_id}")

        for dependency in requires:
            if not isinstance(dependency, str):
                raise ResolveError(f"Invalid dependency in {module_id}")
            visit(dependency)

        temporary.pop()
        permanent.add(module_id)
        ordered.append(module)

    for module_id in selected:
        if not isinstance(module_id, str):
            raise ResolveError(f"Invalid module in profile {profile_id}")
        visit(module_id)

    return ordered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument(
        "--secrets",
        action="store_true",
        help="Print required secret identifiers instead of module ids.",
    )
    args = parser.parse_args()

    try:
        modules = resolve_profile(args.repo.resolve(), args.profile)
    except ResolveError as exc:
        print(f"[cloudstack] ERROR: {exc}", file=sys.stderr)
        return 1

    if args.secrets:
        seen: set[str] = set()

        for module in modules:
            for secret in module.get("secrets", []):
                if secret not in seen:
                    seen.add(secret)
                    print(secret)
    else:
        for module in modules:
            print(module["id"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
