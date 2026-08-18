# ADR-0002: Modular architecture

Status: Accepted

## Decision

Cloud Stack is composed of independent modules grouped by capability.

Examples:

- `core/`
- `data/`
- `identity/`
- `endpoint/`
- `mail/`
- `security/`
- `workplace/`

Modules may depend on other modules.

## Consequences

- Services can be installed and maintained independently.
- Shared infrastructure is reused through declared dependencies.
- New capabilities should normally be implemented as modules.