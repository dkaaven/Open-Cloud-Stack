#!/usr/bin/env bash
set -Eeuo pipefail

MIN_PODMAN_VERSION="5.0.0"

log() {
    echo "[cloudstack] $*"
}

fail() {
    echo "[cloudstack] ERROR: $*" >&2
    exit 1
}

# Must run on Linux
[[ "$(uname -s)" == "Linux" ]] || fail "Linux is required."

# Detect distro
[[ -f /etc/os-release ]] || fail "Unable to detect Linux distribution."
source /etc/os-release

case "${ID:-}" in
    ubuntu|debian)
        ;;
    *)
        fail "Unsupported distribution: ${ID:-unknown}. Currently supports Ubuntu/Debian."
        ;;
esac

log "Detected: ${PRETTY_NAME:-$ID}"

# Install Podman
if ! command -v podman >/dev/null 2>&1; then
    log "Installing Podman..."

    sudo apt-get update
    sudo apt-get install -y \
        podman \
        uidmap \
        fuse-overlayfs
else
    log "Podman already installed."
fi

PODMAN_VERSION="$(podman version --format '{{.Client.Version}}' 2>/dev/null || podman --version | awk '{print $3}')"

log "Podman version: $PODMAN_VERSION"

if ! dpkg --compare-versions "$PODMAN_VERSION" ge "$MIN_PODMAN_VERSION"; then
    fail "Podman >= $MIN_PODMAN_VERSION required. Installed: $PODMAN_VERSION"
fi

# Quadlet requires cgroup v2
CGROUP_VERSION="$(podman info --format '{{.Host.CgroupsVersion}}' 2>/dev/null || true)"

if [[ "$CGROUP_VERSION" != "v2" ]]; then
    fail "Cloud Stack requires cgroup v2. Detected: ${CGROUP_VERSION:-unknown}"
fi

log "cgroup v2: OK"

# System Quadlet directory
sudo install -d -m 0755 /etc/containers/systemd

# Cloud Stack configuration/data locations
sudo install -d -m 0755 /etc/cloudstack
sudo install -d -m 0755 /var/lib/cloudstack

# Make sure systemd sees Quadlets
sudo systemctl daemon-reload

log "Testing Podman..."
podman info >/dev/null

echo
echo "Podman installation OK"
echo
echo "  Version:        $PODMAN_VERSION"
echo "  cgroup:         $CGROUP_VERSION"
echo "  Quadlet path:   /etc/containers/systemd"
echo "  Config path:    /etc/cloudstack"
echo "  Data path:      /var/lib/cloudstack"
echo
