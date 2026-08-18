# Architecture

Cloud Stack is a modular application platform built on Podman, Quadlet and systemd.

## Runtime

- Podman runs containers.
- Quadlet defines containers, networks, volumes and related resources.
- systemd manages lifecycle.
- Kubernetes is not required.

## Modules

Modules provide deployable capabilities.

```text
modules/<category>/<module>/
```

Each module contains a machine-readable `module.yaml`.

Modules may depend on other modules.

## Profiles

Profiles define which modules make up an installation.

Profiles select modules. Module dependencies are resolved from `module.yaml`.

## Networking

`core/network` owns shared platform networks.

```text
cloudstack-edge    ingress and application traffic
cloudstack-data    shared data services
```

Modules declare their required network roles.

## Configuration

Repository defaults and module configuration are stored in source.

Deployment-specific configuration and secrets are kept separate from source.

## Runtime state

Cloud Stack separates:

- source
- configuration
- secrets
- persistent application data

## Design principles

- Modular
- Reproducible
- Secure by default
- Standards based
- Open source where practical
- No Kubernetes dependency
- Simple to operate
