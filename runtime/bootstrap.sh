#!/usr/bin/env bash
set -Eeuo pipefail

readonly REPOSITORY="https://github.com/dkaaven/Open-Cloud-Stack.git"
readonly INSTALL_DIR="/opt/open-cloud-stack"
readonly BRANCH="${CLOUDSTACK_BRANCH:-main}"
readonly PROFILE="${CLOUDSTACK_PROFILE:-core}"

log() {
    printf '[cloudstack] %s\n' "$*"
}

die() {
    printf '[cloudstack] ERROR: %s\n' "$*" >&2
    exit 1
}

if [[ "${EUID}" -ne 0 ]]; then
    cat >&2 <<'EOF'
Cloud Stack installation requires root privileges.

Run:

  curl -fsSL https://raw.githubusercontent.com/dkaaven/Open-Cloud-Stack/main/runtime/bootstrap.sh | sudo bash
EOF
    exit 1
fi

[[ -r /etc/os-release ]] || die "/etc/os-release not found."

# shellcheck disable=SC1091
source /etc/os-release

[[ "${ID:-}" == "debian" ]] || die "Debian is required."
[[ "${VERSION_ID:-}" == "13" ]] || die "Debian 13 is required."

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

log "Preparing Podman runtime..."
"${INSTALL_DIR}/runtime/install-podman.sh"

log "Installing Cloud Stack profile: ${PROFILE}"
exec "${INSTALL_DIR}/runtime/install-stack.sh" --profile "${PROFILE}"
