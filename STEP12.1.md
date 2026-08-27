# Step 12.1: Module host requirement preflight

Live Valkey testing confirmed the additional host requirement:

```text
vm.overcommit_memory=1
```

Step 12.1 makes host prerequisite checks a generic part of the module
installation lifecycle.

## Apply

From the repository root:

```bash
rsync -av   ~/Downloads/cloudstack-runtime-step12-1-host-requirements/   ./

./apply-step12-1.py
rm apply-step12-1.py

uv run pytest
```

Then:

```bash
git add .
git commit -m "feat: add module host requirement preflight"
git push
```

## Installer behavior

A module can provide:

```text
health/check-host.sh
```

The installer runs this check for every resolved module before touching the
currently installed stack.

For the `platform` profile, expected early output is:

```text
[cloudstack] Checking host requirements: data/valkey
[cloudstack] vm.overcommit_memory=1: OK
```

If the requirement is not satisfied, installation stops without stopping the
currently running workloads.

## Proxmox

The central host setup is documented at:

```text
docs/platforms/proxmox-lxc.md
```
