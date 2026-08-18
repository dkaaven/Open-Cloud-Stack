#!/usr/bin/env bash
set -Eeuo pipefail

if (( EUID != 0 )); then
    exec sudo "$0" "$@"
fi

QUADLET_ROOT="/etc/containers/systemd/cloudstack/core"
CONFIG_ROOT="/etc/cloudstack/modules/core"
RUNTIME_ROOT="/etc/cloudstack/runtime"

TARGET_FILE="/etc/systemd/system/cloudstack-core.target"
WORKLOAD_MANIFEST="$RUNTIME_ROOT/core.workloads"
UNIT_MANIFEST="$RUNTIME_ROOT/core.units"

PURGE_CONFIG=false

if [[ "${1:-}" == "--purge-config" ]]; then
    PURGE_CONFIG=true
fi

echo "[cloudstack] Stopping Cloud Stack Core..."

systemctl disable --now cloudstack-core.target 2>/dev/null || true

# Remove generated PartOf drop-ins.
if [[ -f "$WORKLOAD_MANIFEST" ]]; then
    while IFS= read -r unit; do
        [[ -n "$unit" ]] || continue

        rm -f "/etc/systemd/system/${unit}.d/10-cloudstack-core.conf"
        rmdir "/etc/systemd/system/${unit}.d" 2>/dev/null || true
    done < "$WORKLOAD_MANIFEST"
fi

echo "[cloudstack] Removing Quadlet definitions..."

rm -rf "$QUADLET_ROOT"
rm -f "$TARGET_FILE"
rm -f "$WORKLOAD_MANIFEST"
rm -f "$UNIT_MANIFEST"

rmdir "$RUNTIME_ROOT" 2>/dev/null || true

if $PURGE_CONFIG; then
    echo "[cloudstack] Removing Core configuration..."
    rm -rf "$CONFIG_ROOT"
else
    echo "[cloudstack] Configuration preserved: $CONFIG_ROOT"
fi

systemctl daemon-reload
systemctl reset-failed >/dev/null 2>&1 || true

echo
echo "Cloud Stack Core uninstalled."
echo
echo "Persistent Podman volumes and /var/lib/cloudstack were NOT deleted."
