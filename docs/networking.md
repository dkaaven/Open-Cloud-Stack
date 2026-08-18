# Networking

Networks are defined by `core/network` and implemented with Podman Quadlet.

## Networks

```text
edge    cloudstack-edge    ingress and application traffic
data    cloudstack-data    shared data services
```

`data` is internal.

## Module membership

Modules declare network roles in `module.yaml`.

Example:

```yaml
networks:
  - edge
  - data
```

Network membership must be explicit.

## Rules

- Traefik uses `edge`.
- PostgreSQL and Valkey use `data`.
- Applications may use both.
- Data services must not use `edge` unless explicitly designed to do so.
- Host-published ports should be exceptional.
