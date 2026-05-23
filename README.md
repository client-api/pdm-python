# clientapi_pdm

Python SDK for the Proxmox Datacenter Manager API. Generated
from the upstream `apidoc.js` from Proxmox Datacenter Manager via [openapi-generator-cli][gen] with
custom Mustache template overrides.

> **Not an official Proxmox project.** Community SDK derived from the
> upstream `apidoc.js`. Always verify against the upstream API viewer.
> <https://pdm.proxmox.com/>.

Requires Python ≥ 3.9.

## Install

```bash
pip install clientapi-pdm
```

Or for development:

```bash
pip install -r requirements.txt
```

## Usage

```python
from clientapi_pdm import Configuration, Pve

cfg = Configuration(
    host='https://pdm1.example.com:8443/api2/json',
    api_key={'Authorization': 'PDMAPIToken=user@realm!tokenid=uuid-secret'},
)
pdm = Pdm(configuration=cfg)

# Per-tag properties are lazily instantiated and share the same ApiClient.
# `removeOperationIdPrefix=true` strips the tag prefix from method names,
# so the call is `pdm.qemu.vm_status(...)`, not `pdm.qemu.qemu_vm_status(...)` —
# you're already inside the `qemu` namespace.
status = pdm.qemu.vm_status(node='pdm1', vmid=100)
nodes = pdm.nodes.get_nodes()
```

### Discovering available methods

Each per-tag API class lives at `clientapi_pdm.api.<tag>_api.<Tag>Api`.
List its methods to see what's callable:

```python
print([m for m in dir(pdm.qemu) if not m.startswith('_')])
```

Generated method-level docstrings explain parameters; the upstream
endpoint reference is the upstream API viewer.

The unified `Pdm` class wraps each per-tag API class (`QemuApi`,
`LxcApi`, `ClusterApi`, `NodesApi`, …) so consumers don't need to
instantiate them individually.

## Compound configs

PVE encodes many fields as CLI-style shorthand strings
(`net0=virtio,bridge=vmbr0,firewall=1`). Round-trip helpers are
emitted for every compound config schema:

```python
from clientapi_pdm.models import PveQemuNetConfig

cfg = PveQemuNetConfig(model='virtio', bridge='vmbr0', firewall=1)
shorthand = cfg.to_shorthand()  # → 'virtio,bridge=vmbr0,firewall=1'

parsed = PveQemuNetConfig.from_shorthand(shorthand)
```

## Indexed families

Numbered properties (`net0..net31`, `mp0..mp255`, …) are exposed on
every model as a single collapsed `nets` / `mps` / … field:

```python
req = QemuCreateVmRequest(
    nets={
        0: 'virtio,bridge=vmbr0',
        3: 'e1000,bridge=vmbr1',
    },
)
# Wire format: { 'net0': 'virtio,bridge=vmbr0', 'net3': 'e1000,bridge=vmbr1' }
```

## License

Apache 2.0 — see [LICENSE](./LICENSE).

[gen]: https://openapi-generator.tech
[upstream-docs]: https://pdm.proxmox.com/
