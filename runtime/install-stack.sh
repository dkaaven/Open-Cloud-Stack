#!/usr/bin/env bash
set -Eeuo pipefail

if (( EUID != 0 )); then
    exec sudo "$0" "$@"
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

CORE_SOURCE="$REPO_ROOT/modules/core"

QUADLET_ROOT="/etc/containers/systemd/cloudstack/core"
CONFIG_ROOT="/etc/cloudstack/modules/core"
RUNTIME_ROOT="/etc/cloudstack/runtime"

TARGET_FILE="/etc/systemd/system/cloudstack-core.target"
UNIT_MANIFEST="$RUNTIME_ROOT/core.units"
WORKLOAD_MANIFEST="$RUNTIME_ROOT/core.workloads"

log() {
    echo "[cloudstack] $*"
}

fail() {
    echo "[cloudstack] ERROR: $*" >&2
    exit 1
}

quadlet_to_unit() {
    local file
    file="$(basename "$1")"

    case "$file" in
        *.container)
            echo "${file%.container}.service"
            ;;
        *.pod)
            echo "${file%.pod}-pod.service"
            ;;
        *.network)
            echo "${file%.network}-network.service"
            ;;
        *.volume)
            echo "${file%.volume}-volume.service"
            ;;
        *)
            return 1
            ;;
    esac
}

command -v podman >/dev/null || fail "Podman is not installed."
command -v systemctl >/dev/null || fail "systemd is required."

[[ -d "$CORE_SOURCE" ]] || fail "Core modules not found: $CORE_SOURCE"

log "Installing Cloud Stack Core"
log "Repository: $REPO_ROOT"

# Remove old Cloud Stack workload drop-ins.
if [[ -f "$WORKLOAD_MANIFEST" ]]; then
    while IFS= read -r unit; do
        [[ -n "$unit" ]] || continue

        rm -f "/etc/systemd/system/${unit}.d/10-cloudstack-core.conf"
        rmdir "/etc/systemd/system/${unit}.d" 2>/dev/null || true
    done < "$WORKLOAD_MANIFEST"
fi

# Rebuild installed Quadlet definitions.
rm -rf "$QUADLET_ROOT"

install -d -m 0755 \
    "$QUADLET_ROOT" \
    "$CONFIG_ROOT" \
    "$RUNTIME_ROOT"

TMP_UNITS="$(mktemp)"
TMP_WORKLOADS="$(mktemp)"

trap 'rm -f "$TMP_UNITS" "$TMP_WORKLOADS"' EXIT

COUNT=0

while IFS= read -r -d '' file; do
    relative="${file#$CORE_SOURCE/}"
    module="${relative%%/*}"
    filename="$(basename "$file")"

    destination="$QUADLET_ROOT/$module/$filename"

    install -D -m 0644 "$file" "$destination"

    unit="$(quadlet_to_unit "$file")"
    echo "$unit" >> "$TMP_UNITS"

    case "$file" in
        *.container|*.pod)
            echo "$unit" >> "$TMP_WORKLOADS"
            ;;
    esac

    ((COUNT+=1))
done < <(
    find "$CORE_SOURCE" \
        -type f \
        -path '*/quadlet/*' \
        \( \
            -name '*.container' -o \
            -name '*.pod'       -o \
            -name '*.network'   -o \
            -name '*.volume' \
        \) \
        -print0
)

(( COUNT > 0 )) || fail "No Core Quadlet files found under modules/core/*/quadlet/"

# Check for duplicate generated systemd unit names.
DUPLICATES="$(sort "$TMP_UNITS" | uniq -d || true)"

if [[ -n "$DUPLICATES" ]]; then
    echo "$DUPLICATES" >&2
    fail "Duplicate systemd unit names detected."
fi

sort -u "$TMP_UNITS" > "$UNIT_MANIFEST"
sort -u "$TMP_WORKLOADS" > "$WORKLOAD_MANIFEST"

# Install module configuration.
for module_dir in "$CORE_SOURCE"/*; do
    [[ -d "$module_dir" ]] || continue

    module="$(basename "$module_dir")"
    module_config="$CONFIG_ROOT/$module"

    install -d -m 0755 "$module_config"

    if [[ -f "$module_dir/module.yaml" ]]; then
        install -m 0644 \
            "$module_dir/module.yaml" \
            "$module_config/module.yaml"
    fi

    if [[ -d "$module_dir/config" ]]; then
        rm -rf "$module_config/config"
        mkdir -p "$module_config/config"
        cp -a "$module_dir/config/." "$module_config/config/"
        chown -R root:root "$module_config/config"
    fi

    # Quadlet drop-ins must sit beside their Quadlet definitions.
    if [[ -d "$module_dir/dropins" ]]; then
        cp -a "$module_dir/dropins/." "$QUADLET_ROOT/$module/"
        chown -R root:root "$QUADLET_ROOT/$module"
    fi
done

# Generate the Core target.
{
    echo "[Unit]"
    echo "Description=Cloud Stack Core"
    echo "Documentation=https://github.com/"
    echo
    echo "Wants=network-online.target"
    echo "After=network-online.target"

    while IFS= read -r unit; do
        [[ -n "$unit" ]] && echo "Wants=$unit"
    done < "$WORKLOAD_MANIFEST"

    echo
    echo "[Install]"
    echo "WantedBy=multi-user.target"
} > "$TARGET_FILE"

# Make stopping/restarting Core propagate to workloads.
while IFS= read -r unit; do
    [[ -n "$unit" ]] || continue

    install -d -m 0755 "/etc/systemd/system/${unit}.d"

    cat > "/etc/systemd/system/${unit}.d/10-cloudstack-core.conf" <<DROPIN
[Unit]
PartOf=cloudstack-core.target
DROPIN
done < "$WORKLOAD_MANIFEST"

log "Reloading systemd..."
systemctl daemon-reload

log "Checking generated Quadlet units..."

FAILED=0

while IFS= read -r unit; do
    [[ -n "$unit" ]] || continue

    if systemctl cat "$unit" >/dev/null 2>&1; then
        printf "  ✓ %s\n" "$unit"
    else
        printf "  ✗ %s\n" "$unit"
        FAILED=1
    fi
done < "$UNIT_MANIFEST"

if (( FAILED )); then
    echo
    fail "One or more Quadlets failed to generate."
fi

echo
echo "Cloud Stack Core installed."
echo
echo "Start:"
echo "  sudo systemctl start cloudstack-core.target"
echo
echo "Start automatically at boot:"
echo "  sudo systemctl enable --now cloudstack-core.target"
echo
echo "Status:"
echo "  ./scripts/status.sh"
