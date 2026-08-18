#!/usr/bin/env bash
set -Eeuo pipefail

if (( EUID != 0 )); then
    exec sudo "$0" "$@"
fi

RUNTIME_ROOT="/etc/cloudstack/runtime"
UNIT_MANIFEST="$RUNTIME_ROOT/core.units"
WORKLOAD_MANIFEST="$RUNTIME_ROOT/core.workloads"
TARGET="cloudstack-core.target"

echo "Cloud Stack"
echo "==========="
echo

if [[ ! -f "$UNIT_MANIFEST" ]]; then
    echo "Status: NOT INSTALLED"
    echo
    echo "Run:"
    echo "  sudo ./scripts/install-stack.sh"
    exit 1
fi

TARGET_STATE="$(systemctl is-active "$TARGET" 2>/dev/null || true)"
TARGET_ENABLED="$(systemctl is-enabled "$TARGET" 2>/dev/null || true)"

printf "%-18s %s\n" "Core:" "$TARGET_STATE"
printf "%-18s %s\n" "Boot:" "$TARGET_ENABLED"
printf "%-18s %s\n" "Podman:" "$(podman --version)"
echo

echo "Units"
echo "-----"

FAILED=0

while IFS= read -r unit; do
    [[ -n "$unit" ]] || continue

    state="$(systemctl is-active "$unit" 2>/dev/null || true)"
    substate="$(systemctl show "$unit" -p SubState --value 2>/dev/null || true)"

    printf "%-42s %-12s %s\n" \
        "$unit" \
        "${state:-unknown}" \
        "${substate:-unknown}"

    case "$state" in
        failed)
            FAILED=1
            ;;
    esac
done < "$UNIT_MANIFEST"

echo
echo "Containers"
echo "----------"

podman ps \
    --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' \
    || true

echo
echo "Pods"
echo "----"

podman pod ps \
    --format 'table {{.Name}}\t{{.Status}}\t{{.Created}}' \
    || true

echo
echo "Failed units"
echo "------------"

FOUND_FAILED=false

while IFS= read -r unit; do
    [[ -n "$unit" ]] || continue

    if [[ "$(systemctl is-failed "$unit" 2>/dev/null || true)" == "failed" ]]; then
        echo "$unit"
        FOUND_FAILED=true
    fi
done < "$UNIT_MANIFEST"

if ! $FOUND_FAILED; then
    echo "None"
fi

echo

if (( FAILED )); then
    exit 1
fi
