# Configuration

Cloud Stack separates source configuration from deployment-specific configuration.

## Source configuration

Stored in the repository:

```text
defaults/
modules/*/config/
modules/*/dropins/
profiles/
```

These files define project and module defaults.

## Deployment configuration

Deployment-specific values are stored outside the source tree.

Default location:

```text
/etc/cloudstack/
```

Examples:

```text
stack.env
customer.env
```

## Persistent data

Application data is stored separately from configuration.

Default location:

```text
/var/lib/cloudstack/
```

## Secrets

Secret values must not be committed to the repository.

Modules declare required secrets, while deployments provide their values separately.

## Rules

* Configuration must be deterministic.
* Deployment-specific values must not modify module source.
* Secrets and persistent data must remain separate from source.
* Configuration precedence must be explicitly defined.
