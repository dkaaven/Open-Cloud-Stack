# ADR-0004: Machine-readable module manifest

Status: Accepted

## Decision

Every module must contain a `module.yaml`.

`module.yaml` is the machine-readable contract for the module.

Human documentation belongs in `README.md`.

The manifest format is versioned independently from Cloud Stack releases.

## Consequences

Module metadata and dependencies can be validated and consumed by tooling.

Example:

```yaml
schema: 1

id: workplace/nextcloud
name: Nextcloud

requires:
  - core/network
  - core/traefik
  - data/postgres
  - data/valkey