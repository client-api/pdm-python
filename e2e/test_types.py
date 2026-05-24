"""SC-50 / SC-51 — type-correctness checks on the generated SDK."""
from __future__ import annotations

import typing

from clientapi_pdm import Pdm
from clientapi_pdm.models.nodes_status_get_status_response_data_memory import (
    NodesStatusGetStatusResponseDataMemory,
)


def test_int64_fields_are_python_int() -> None:
    """SC-50 — bytes counters round-trip as `int`, not `float`.

    Static check that datastore status fields are typed `int`.
    """
    hints = typing.get_type_hints(NodesStatusGetStatusResponseDataMemory)
    for field in ("free", "total", "used"):
        annotation = hints[field]
        members = typing.get_args(annotation) or (annotation,)
        assert any(m is int or getattr(m, "__name__", "") == "StrictInt" for m in members), (
            f"{field} annotation is {annotation!r} — must include int"
        )


def test_nullable_fields_deserialize_to_none(pdm: Pdm) -> None:
    """SC-51 — Optional fields that the server omits arrive as `None`.

    PDM happens to seed all users with a non-null `comment`, so this test
    probes a different shape: `firstname` is Optional[str] and unset by
    default.
    """
    users = pdm.accessUsers.get_users().data or []
    assert users, "expected at least one user"
    omitted = [u for u in users if getattr(u, "firstname", None) is None]
    assert omitted, (
        "no user had a None firstname — model may be silently coercing "
        "Optional fields to empty string"
    )
