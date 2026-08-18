# Modules

Modules are the deployable building blocks of Cloud Stack.

## Location

```text
modules/<category>/<module>/
```

## Required files

Every module must contain:

```text
module.yaml
README.md
```

`module.yaml` defines the machine-readable module contract.

## Optional directories

```text
quadlet/    Quadlet definitions
config/     Default configuration
dropins/    Quadlet/systemd overrides
health/     Health checks
backup/     Backup and restore tooling
```

Only directories used by the module should exist.

## Dependencies

Dependencies are declared in `module.yaml`.

## Networks

Network membership is declared in `module.yaml`.

## Storage

Persistent storage is declared in `module.yaml`.

Storage marked `backup: true` requires backup and restore support.

## Rules

- Modules must be independently understandable.
- Deployment-specific secrets must not be stored in modules.
- Persistent state must be explicit.
- Network membership must be explicit.
- Architectural decisions belong in ADRs.
