# Valkey

Cloud Stack uses Valkey for Redis-compatible caching and distributed locking.

## Deployment

Valkey is part of the `platform` profile and joins only `cloudstack-data`.

## Authentication

Create the required deployment secret:

```bash
install -d -m 0700 /etc/cloudstack/secrets
umask 077
openssl rand -hex 32 > /etc/cloudstack/secrets/valkey-password
chmod 0600 /etc/cloudstack/secrets/valkey-password
```

The server generates an ephemeral ACL from the Podman-mounted secret. The
password is not passed as a Valkey command-line argument.

## Persistence

Append-only persistence is enabled on the named Valkey volume.

This improves continuity across restarts, but Valkey remains non-authoritative
cache/locking data and its volume is not backup-required.

## Kernel setting

Valkey recommends:

```text
vm.overcommit_memory=1
```

Check:

```bash
modules/data/valkey/health/check-host.sh
```

Cloud Stack does not silently modify a host-wide kernel setting from an LXC
guest.

## Exposure

Valkey has no published host port. Applications use `cloudstack-data`.
