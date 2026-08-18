from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"
NETWORK_QUADLETS = MODULES / "core" / "network" / "quadlet"

NETWORKS = {
    "edge": "cloudstack-edge.network",
    "data": "cloudstack-data.network",
}

DEPENDENCY_NETWORKS = {
    "core/traefik": "edge",
    "data/postgres": "data",
    "data/valkey": "data",
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def module_files() -> list[Path]:
    return sorted(MODULES.glob("*/*/module.yaml"))


def test_shared_network_quadlets_exist():
    for filename in NETWORKS.values():
        assert (NETWORK_QUADLETS / filename).is_file()


def test_edge_network_has_stable_name():
    content = (NETWORK_QUADLETS / NETWORKS["edge"]).read_text(encoding="utf-8")

    assert "NetworkName=cloudstack-edge" in content


def test_data_network_has_stable_name_and_is_internal():
    content = (NETWORK_QUADLETS / NETWORKS["data"]).read_text(encoding="utf-8")

    assert "NetworkName=cloudstack-data" in content
    assert "Internal=true" in content


def test_network_module_does_not_join_managed_networks():
    data = load_yaml(MODULES / "core" / "network" / "module.yaml")

    assert data["networks"] == []


def test_traefik_uses_only_edge():
    data = load_yaml(MODULES / "core" / "traefik" / "module.yaml")

    assert data["networks"] == ["edge"]


def test_postgres_uses_only_data():
    data = load_yaml(MODULES / "data" / "postgres" / "module.yaml")

    assert data["networks"] == ["data"]


def test_valkey_uses_only_data():
    data = load_yaml(MODULES / "data" / "valkey" / "module.yaml")

    assert data["networks"] == ["data"]


def test_dependency_network_requirements():
    failures = []

    for manifest in module_files():
        module = load_yaml(manifest)
        networks = set(module["networks"])

        for dependency in module["requires"]:
            required_network = DEPENDENCY_NETWORKS.get(dependency)

            if required_network and required_network not in networks:
                failures.append(
                    f"{module['id']} requires {dependency} "
                    f"but does not declare network {required_network}"
                )

    assert not failures, "\n".join(failures)

# def quadlet(path: str) -> str:
#     return (ROOT / path).read_text(encoding="utf-8")


# def test_nextcloud_network_membership():
#     content = quadlet(
#         "modules/workplace/nextcloud/quadlet/nextcloud.container"
#     )

#     assert "Network=cloudstack-edge.network" in content
#     assert "Network=cloudstack-data.network" in content


# def test_nextcloud_cron_network_membership():
#     content = quadlet(
#         "modules/workplace/nextcloud/quadlet/nextcloud-cron.container"
#     )

#     assert "Network=cloudstack-data.network" in content
#     assert "Network=cloudstack-edge.network" not in content