# ADR-0007: Network architecture

Status: Accepted

## Decision

Cloud Stack uses shared Podman networks owned by `core/network`.

Two network roles are defined:

- `edge` for ingress and application traffic.
- `data` for shared data services.

The runtime network names are:

```text
cloudstack-edge
cloudstack-data
```

`cloudstack-data` is internal and must not provide external network access.

Modules declare required network roles in `module.yaml`.

## Consequences

- Traefik uses `edge`.
- PostgreSQL and Valkey use `data`.
- Applications may use both.
- Data services are not attached to `edge`.
- Additional network roles require an architectural decision.
