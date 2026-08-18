# Network

Provides the shared Cloud Stack Podman networks.

## Resources

```text
cloudstack-edge    ingress and application traffic
cloudstack-data    internal shared data traffic
```

`cloudstack-data` does not provide external network access.

## Quadlets

```text
quadlet/cloudstack-edge.network
quadlet/cloudstack-data.network
```

The network module does not run containers and has no persistent state.
