# ADR-0015: Reconcile runtime resources before workloads

Status: Accepted

## Context

Quadlet network and volume units are one-shot systemd services.

A resource unit may remain active even if the underlying Podman resource has
been removed outside systemd.

## Decision

Cloud Stack records resource units separately from workload units.

After installing Quadlet definitions and running `systemctl daemon-reload`,
the installer explicitly restarts every installed resource unit before
starting Cloud Stack workloads.

Resource units currently include:

- `.network`
- `.volume`

Workload units currently include:

- `.container`
- `.pod`

## Consequences

- Installed Podman resources are reconciled on every stack installation.
- Workloads are started only after resource reconciliation succeeds.
- Persistent data is not explicitly deleted by the installer or uninstaller.
