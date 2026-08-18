# Security

Cloud Stack is secure by default.

## Baseline

* Containers should run with least privilege.
* `no-new-privileges` should be enabled by default.
* Privileged containers require explicit justification.
* Network exposure must be intentional.
* Secrets must not be stored in source control.
* Container images must use explicit versions.
* Persistent data must be explicitly defined.
* Stateful modules must support backup and restore.

## Defaults

Shared security policy belongs in:

```text
defaults/container.d/
```

Module-specific exceptions must be documented.

## Scope

Cloud Stack provides technical security controls.

Compliance requirements and framework mappings are documented separately.
