# Operations

Cloud Stack lifecycle is managed through systemd and the runtime tooling.

## Lifecycle

Core operations are:

```text
install
validate
start
stop
restart
status
upgrade
backup
restore
uninstall
```

## Runtime tooling

Runtime scripts and tooling live in:

```text
runtime/
```

They must operate on declared modules and profiles rather than contain service-specific configuration.

## systemd

systemd is the lifecycle authority for deployed Cloud Stack services.

Quadlet-generated units must be managed through systemd.

## Rules

* Operations must be repeatable.
* Failed operations should return a non-zero exit code.
* Uninstall must not remove persistent data unless explicitly requested.
* Stateful modules must provide documented backup and restore procedures.
