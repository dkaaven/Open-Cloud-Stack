#!/bin/sh
set -eu

secret="/run/secrets/valkey-password"
acl="/tmp/cloudstack-valkey-users.acl"

if [ ! -r "${secret}" ]; then
    printf '[cloudstack] ERROR: Valkey password secret is not readable.\n' >&2
    exit 1
fi

password="$(cat "${secret}")"

if [ -z "${password}" ]; then
    printf '[cloudstack] ERROR: Valkey password secret is empty.\n' >&2
    exit 1
fi

case "${password}" in
    *[!0-9A-Fa-f]*)
        printf '[cloudstack] ERROR: Valkey password must be hexadecimal.\n' >&2
        exit 1
        ;;
esac

if [ "${#password}" -lt 64 ]; then
    printf '[cloudstack] ERROR: Valkey password must contain at least 64 hexadecimal characters.\n' >&2
    exit 1
fi

umask 077
printf 'user default on >%s ~* +@all\n' "${password}" > "${acl}"

exec valkey-server /etc/valkey/valkey.conf
