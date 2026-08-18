# ADR-0005: Configuration precedence

Status: Accepted

## Decision

Configuration is applied in this order, with later sources overriding earlier sources:

1. Cloud Stack defaults
2. Module defaults
3. `/etc/cloudstack/stack.env`
4. `/etc/cloudstack/customer.env`

Source configuration must not contain deployment-specific values.

## Consequences

- Configuration resolution is deterministic.
- Deployment configuration stays outside the repository.
- Modules must not modify configuration precedence.
