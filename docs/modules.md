# Modules

Modules are the deployable building blocks of Cloud Stack.

## Location

```text
modules/<category>/<module>/
```

Example:

```text
modules/workplace/nextcloud/
```

## Required files

Every module must contain:

```text
module.yaml
README.md
```

`module.yaml` defines the machine-readable module contract.

`README.md` contains module-specific technical documentation.

## Optional directories

A module may contain:

```text
quadlet/    Quadlet definitions
config/     Default configuration
dropins/    Quadlet/systemd overrides
health/     Health checks
backup/     Backup and restore tooling
```

Only directories used by the module should exist.

## Dependencies

Module dependencies are declared in `module.yaml`.

Example:

```yaml
requires:
  - core/network
  - core/traefik
  - data/postgres
```

Profiles must not duplicate transitive dependencies.

## Rules

* Modules must be independently understandable.
* Modules must not contain deployment-specific secrets.
* Persistent state must be explicit.
* Module resources should use the `cloudstack-` namespace where applicable.
* Architectural decisions belong in ADRs.
