# Valkey

Cloud Stack uses Valkey for Redis-compatible caching and distributed locking.

## Deployment

Valkey is part of the `platform` profile and joins only `cloudstack-data`.

When a selected profile includes Valkey, `install-stack.sh` runs its host
requirement check before changing the running Cloud Stack deployment.

## Authentication

Create the required deployment secret:

```bash
install -d -m 0700 /etc/cloudstack/secrets
umask 077

openssl rand -hex 32   > /etc/cloudstack/secrets/valkey-password

chmod 0600   /etc/cloudstack/secrets/valkey-password
```

The server generates an ephemeral ACL from the Podman-mounted secret. The
password is not passed as a Valkey command-line argument.

## Persistence

Append-only persistence is enabled on the named Valkey volume.

This improves continuity across restarts, but Valkey remains non-authoritative
cache/locking data and its volume is not backup-required.

## Host requirement

Valkey requires:

```text
vm.overcommit_memory=1
```

Verify:

```bash
modules/data/valkey/health/check-host.sh
```

For Proxmox LXC, configure the setting on the Proxmox host:

```text
docs/platforms/proxmox-lxc.md
```

Cloud Stack does not silently modify a host-wide kernel setting from an LXC
guest.

## Exposure

Valkey has no published host port. Applications communicate with it through
`cloudstack-data`.
