#!/usr/bin/env bash
set -Eeuo pipefail

value="$(sysctl -n vm.overcommit_memory 2>/dev/null || true)"

if [[ "${value}" == "1" ]]; then
    printf '[cloudstack] vm.overcommit_memory=1: OK\n'
    exit 0
fi

printf '[cloudstack] WARNING: vm.overcommit_memory=%s; Valkey recommends 1.\n' \
    "${value:-unknown}" >&2

if [[ "$(systemd-detect-virt --container 2>/dev/null || true)" == "lxc" ]]; then
    printf '[cloudstack] In LXC this may need to be configured on the virtualization host.\n' >&2
fi

exit 1
