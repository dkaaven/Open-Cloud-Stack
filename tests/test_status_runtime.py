from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "runtime" / "status.sh"


def test_status_reports_resources_and_workloads_separately():
    content = STATUS.read_text(encoding="utf-8")

    assert 'RESOURCE_MANIFEST="${RUNTIME_ROOT}/resources"' in content
    assert 'WORKLOAD_MANIFEST="${RUNTIME_ROOT}/workloads"' in content
    assert "printf '\\nResources\\n'" in content
    assert "printf '\\nWorkloads\\n'" in content
    assert 'print_unit_manifest "${RESOURCE_MANIFEST}"' in content
    assert 'print_unit_manifest "${WORKLOAD_MANIFEST}"' in content
