# Configuration

Cloud Stack separates source configuration from deployment configuration.

## Source

```text
defaults/
modules/*/config/
modules/*/dropins/
profiles/
```

## Deployment

```text
/etc/cloudstack/
├── stack.env
├── customer.env
└── secrets/
```

Configuration precedence, lowest to highest:

1. Cloud Stack defaults
2. Module defaults
3. `stack.env`
4. `customer.env`

## State

Persistent application data lives under:

```text
/var/lib/cloudstack/
```

## Rules

- Deployment values must not be committed.
- Secret values must not be committed.
- Modules may declare secret identifiers in `module.yaml`.
