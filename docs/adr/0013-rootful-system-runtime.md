# ADR-0013: Rootful system runtime

Status: Accepted

## Decision

Cloud Stack runs Podman as a rootful system service.

Quadlets are installed under:

```text
/etc/containers/systemd/
```

Cloud Stack does not require a dedicated runtime user.

## Consequences

- systemd manages Cloud Stack at the system level.
- Privileged host ports can be used directly.
- Podman storage and secrets are system-scoped.
- Rootless Podman is not the primary deployment mode.
