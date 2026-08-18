# ADR-0009: Container image policy

Status: Accepted

## Decision

Deployable container images must use immutable digest references.

Modules declare images in `module.yaml` with a human-readable upstream version and an immutable image reference.

`latest` is not allowed.

## Consequences

- Deployments are reproducible.
- Image updates are explicit repository changes.
- Image versions remain readable without relying on mutable tags.
