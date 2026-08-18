# ADR-0003: Separate modules from profiles

Status: Accepted

## Decision

Modules deploy capabilities.

Profiles select modules to create a desired Cloud Stack installation.

Dependencies belong to modules and must not be duplicated in profiles.

## Consequences

A profile can select:

```yaml
modules:
  - workplace/nextcloud