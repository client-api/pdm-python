"""Example: list cluster nodes.

Run with:
    PDM_HOST=https://pdm.example.com:8443 \\
    PDM_TOKEN='PDMAPIToken=root@pam!auto:...' \\
    python examples/list_nodes.py
"""

from __future__ import annotations

import os

from clientapi_pdm.configuration import Configuration
from clientapi_pdm.pdm import Pdm


def main() -> None:
    config = Configuration(host=f"{os.environ.get('PDM_HOST', 'https://localhost:8443')}/api2/json")
    # OpenAPI auth-scheme name (NOT the `Authorization` header name).
    # The full `PDMAPIToken=…` string goes in here; no api_key_prefix.
    config.api_key["PDMApiToken"] = os.environ.get("PDM_TOKEN", "")

    pdm = Pdm(config)
    response = pdm.nodes.get_nodes()
    nodes = getattr(response, "data", None) or []
    print(f"Found {len(nodes)} node(s):")
    for node in nodes:
        print(
            f"  - {getattr(node, 'node', None)} "
            f"(status={getattr(node, 'status', None)}, "
            f"cpu={getattr(node, 'cpu', None)}, "
            f"mem={getattr(node, 'mem', None)}/{getattr(node, 'maxmem', None)})",
        )


if __name__ == "__main__":
    main()
