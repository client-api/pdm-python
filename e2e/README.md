# E2E tests for `clientapi_pdm`

Live-server pytest suite. Runs against a real Proxmox Datacenter Manager instance —
by default the `ghcr.io/client-api/proxmox-docker/pdm-test` container, either
spun up locally via `docker compose up -d` or in CI via
[`client-api/proxmox-docker-action@v1`](https://github.com/client-api/proxmox-docker-action).

## Quick start (local)

```bash
docker compose up -d
sleep 20  # wait for healthcheck

export PROXMOX_URL=https://localhost:8443
export PROXMOX_USER=root@pam
export PROXMOX_PASSWORD=proxmox123
export PROXMOX_TOKEN_HEADER_VALUE="$(docker exec pdm-test cat /run/credentials.json | jq -r .token_header_value)"
export PROXMOX_INSECURE=1

pip install -e .
pip install 'pytest>=8' 'pytest-timeout>=2.3' requests
pytest e2e/ -v
```

## Scenario index

Universal core scenarios that map cleanly to PDM:

| File | Scenarios |
|---|---|
| `test_version.py` | SC-01 |
| `test_auth.py` | SC-10 (ticket-info shape), SC-11/12/13 (PDM uses `:` token separator); SC-14 skipped (PDM cookie auth is HttpOnly server-set) |
| `test_crud.py` | SC-30, SC-31 (user CRUD) |
| `test_errors.py` | SC-41 (input validation), SC-42 (token without ACL) |
| `test_types.py` | SC-50 (int64 memory counters), SC-51 (nullable) |

PVE-specific scenarios (storage CRUD, ISO upload, VM/CT lifecycle, oneOf
storage discriminator) do not apply to PDM — the suite reference for those
lives in `pve-python/e2e/`.

## Sibling suites

`pve-python` is the canonical suite; `pmg-python` and `pdm-python` follow
the same shape with per-product API and auth differences.
