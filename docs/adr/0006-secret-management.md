# ADR-0006: Secret management

Status: Accepted

## Decision

Modules declare required secret identifiers in `module.yaml`.

Secret identifiers must be scoped to the module and start with the module name.

Secret values are deployment state and must not be stored in the repository.

The default file source is:

```text
/etc/cloudstack/secrets/<secret-id>
```

Runtime tooling is responsible for exposing secret values to Podman.

## Consequences

- Module source contains secret identifiers only.
- Secret values can be supplied independently from source.
- Alternative secret providers may be added later without changing module manifests.
