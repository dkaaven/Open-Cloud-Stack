# Valkey

Valkey provides shared Redis-compatible caching and distributed locking.

## Runtime

Container:

```text
cloudstack-data-valkey
```

Image:

```text
docker.io/valkey/valkey@sha256:ee91f7a174ac4d6a6b0685b3a60e321f0a9dbbb691f9b0e285be2ba1d1be8328
```

The image is pinned by digest.

## Network

Valkey joins only:

```text
cloudstack-data
```

Port `6379` is not published on the host and Valkey is not exposed through
Traefik.

## Authentication

Valkey requires the deployment secret:

```text
/etc/cloudstack/secrets/valkey-password
```

The secret is mounted into the container through Podman secrets.

At startup the non-root process creates an ephemeral ACL file in `/tmp` and
starts Valkey with that ACL. The password is therefore not placed in the
Valkey command line.

## Process privileges

Valkey runs as the image's dedicated user:

```text
uid 999
gid 1000
```

The container uses non-root execution, a read-only root filesystem,
`NoNewPrivileges`, and drops all Linux capabilities.

## Storage

Named volume:

```text
cloudstack-data-valkey-data
```

Container path:

```text
/data
```

Append-only persistence is enabled to preserve operational state across
container restarts and stack reconciliation.

The module declares this state as `backup: false`: Valkey is cache/locking
state, not an authoritative backup dataset.

## Host requirement

Valkey recommends:

```text
vm.overcommit_memory=1
```

Check:

```bash
modules/data/valkey/health/check-host.sh
```

In an unprivileged LXC this setting may need to be configured on the
virtualization host.

## Health

```bash
modules/data/valkey/health/check.sh
```
