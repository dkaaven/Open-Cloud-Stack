#!/bin/sh
set -eu

secret="/run/secrets/valkey-password"
[ -r "${secret}" ] || exit 1

password="$(cat "${secret}")"

response="$(
    valkey-cli \
        --no-auth-warning \
        -a "${password}" \
        ping 2>/dev/null
)"

[ "${response}" = "PONG" ]
