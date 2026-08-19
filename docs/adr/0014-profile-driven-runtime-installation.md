# ADR-0014: Profile-driven runtime installation

Status: Accepted

## Decision

Cloud Stack installation is driven by profiles.

A Python helper resolves module dependencies from `profile.yaml` and `module.yaml`.

Bash remains responsible for filesystem installation, Podman and systemd operations.

Installed profile, modules and generated units are recorded under:

```text
/etc/cloudstack/runtime/
```

## Consequences

- Profiles define installation intent.
- Dependencies are installed automatically.
- Runtime status and uninstall use recorded installation state.
