#!/usr/bin/env bash
set -Eeuo pipefail

readonly REPOSITORY="https://github.com/dkaaven/Open-Cloud-Stack.git"
readonly INSTALL_DIR="/opt/open-cloud-stack"
readonly BRANCH="${CLOUDSTACK_BRANCH:-main}"

log() {
    printf '[cloudstack] %s\n' "$*"
}

die() {
    printf '[cloudstack] ERROR: %s\n' "$*" >&2
    exit 1
}

[[ "${EUID}" -eq 0 ]] || die "Run as root."

[[ -r /etc/os-release ]] || die "/etc/os-release not found."

# shellcheck disable=SC1091
source /etc/os-release

[[ "${ID:-}" == "debian" ]] ||
    die "Debian is required."

[[ "${VERSION_ID:-}" == "13" ]] ||
    die "Debian 13 is required."

log "Installing bootstrap dependencies..."

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
    ca-certificates \
    git

if [[ -d "${INSTALL_DIR}/.git" ]]; then
    log "Updating existing Cloud Stack repository..."

    git -C "${INSTALL_DIR}" fetch origin
    git -C "${INSTALL_DIR}" checkout "${BRANCH}"
    git -C "${INSTALL_DIR}" pull --ff-only origin "${BRANCH}"
else
    log "Downloading Cloud Stack..."

    rm -rf "${INSTALL_DIR}"

    git clone \
        --branch "${BRANCH}" \
        --single-branch \
        "${REPOSITORY}" \
        "${INSTALL_DIR}"
fi

log "Running host installer..."

exec "${INSTALL_DIR}/runtime/install-podman.sh"