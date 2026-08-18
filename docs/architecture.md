# Architecture

Cloud Stack is a modular application platform built on Podman, Quadlet and systemd.

## Runtime

* Podman runs containers.
* Quadlet defines containers, networks, volumes and related resources.
* systemd manages lifecycle.
* Kubernetes is not required.

## Modules

Modules provide deployable capabilities.

```text
modules/<category>/<module>/
```

Examples:

```text
modules/core/traefik
modules/data/postgres
modules/identity/kanidm
modules/workplace/nextcloud
```

Each module contains a machine-readable `module.yaml`.

Modules may depend on other modules.

## Profiles

Profiles define which modules make up an installation.

```text
profiles/
├── core.yaml
├── workplace.yaml
└── managed.yaml
```

Profiles select modules. Module dependencies are resolved from `module.yaml`.

## Configuration

Repository defaults and module configuration are stored in the source tree.

Deployment-specific configuration and secrets are kept separate from source.

## Runtime state

Cloud Stack separates:

* source
* configuration
* secrets
* persistent application data

This allows installations to be reproduced from a known Cloud Stack version, configuration, secrets and backups.

## Design principles

* Modular
* Reproducible
* Secure by default
* Standards based
* Open source where practical
* No Kubernetes dependency
* Simple to operate
