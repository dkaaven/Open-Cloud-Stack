# ADR-0011: Traefik file provider

Status: Accepted

## Decision

Traefik uses the file provider for dynamic routing configuration.

The Podman API socket is not mounted into Traefik.

## Consequences

- Routing configuration is explicit and reproducible.
- Traefik does not require Podman control-plane access.
- Module routes can be installed as files under the Traefik dynamic configuration directory.
