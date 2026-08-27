# Proxmox LXC

Cloud Stack supports Debian 13 in an unprivileged Proxmox LXC where nested
containers are appropriate.

## LXC baseline

Recommended container configuration:

```text
unprivileged=1
features=nesting=1,keyctl=1
```

Configure these on the Proxmox host.

## Valkey kernel requirement

Valkey requires the host prerequisite:

```text
vm.overcommit_memory=1
```

LXC containers use the Proxmox host kernel directly. This is therefore a host
kernel setting, not an isolated setting for one LXC.

Configure it on the **Proxmox host**:

```bash
cat > /etc/sysctl.d/99-cloudstack-valkey.conf <<'EOF'
vm.overcommit_memory=1
EOF

sysctl --system
```

Verify on the Proxmox host:

```bash
sysctl vm.overcommit_memory
```

Expected:

```text
vm.overcommit_memory = 1
```

Then verify inside the Cloud Stack LXC:

```bash
cd /opt/open-cloud-stack

modules/data/valkey/health/check-host.sh
```

Expected:

```text
[cloudstack] vm.overcommit_memory=1: OK
```

Do not have the LXC guest silently modify this setting. It affects the shared
host kernel and can therefore affect other containers on the Proxmox host.
