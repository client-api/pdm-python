"""SC-10 … SC-14 — authentication paths."""
from __future__ import annotations

import pytest

from clientapi_pdm import Configuration, Pdm
from clientapi_pdm.exceptions import ApiException
from clientapi_pdm.models.access_ticket_create_ticket_request import (
    AccessTicketCreateTicketRequest,
)
from e2e.helpers.clients import issue_ticket, ticket_client, token_client
from e2e.helpers.credentials import Credentials


def test_ticket_login_returns_ticket_info_and_csrf(creds: Credentials) -> None:
    """SC-10 — POST /access/ticket yields CSRFPreventionToken (PDM variant).

    PDM uses a stateful 'ticket-info' field instead of a plain ticket cookie;
    classic browser auth is handled by the PDM frontend over a server-set
    HttpOnly cookie. The API-level response carries `ticket_info` plus the
    CSRF token, but no `ticket` field — verify the shape we actually receive.
    """
    anon = Configuration(host=f"{creds.url}/api2/json")
    anon.verify_ssl = not creds.insecure
    pdm = Pdm(anon)

    response = pdm.accessTicket.create_ticket(
        AccessTicketCreateTicketRequest(username=creds.user, password=creds.password)
    )
    data = response.data
    assert data is not None
    assert data.csrf_prevention_token, "CSRFPreventionToken missing"
    assert data.ticket_info, "ticket-info missing"


def test_invalid_password_raises_401(creds: Credentials) -> None:
    """SC-11 — wrong password ⇒ 401."""
    with pytest.raises(ApiException) as excinfo:
        issue_ticket(creds, password="definitely-not-the-password")
    assert excinfo.value.status == 401, excinfo.value


def test_token_auth_lists_users(creds: Credentials) -> None:
    """SC-12 — API-token auth roundtrips against a GET that requires permissions.

    PDM doesn't grant `/nodes` read perms to the default test token; `/access/users`
    is reachable by any authenticated principal.
    """
    pdm = token_client(creds)
    response = pdm.accessUsers.get_users()
    assert getattr(response, "data", None) is not None


def test_malformed_token_raises_401(creds: Credentials) -> None:
    """SC-13 — bogus token UUID ⇒ 401."""
    cfg = Configuration(host=f"{creds.url}/api2/json")
    cfg.verify_ssl = not creds.insecure
    cfg.api_key["PDMApiToken"] = "PDMAPIToken=root@pam!test:00000000-0000-0000-0000-000000000000"
    pdm = Pdm(cfg)
    with pytest.raises(ApiException) as excinfo:
        pdm.accessUsers.get_users()
    assert excinfo.value.status == 401, excinfo.value


@pytest.mark.skip(
    reason=(
        "SC-14 doesn't apply to PDM: the API surface returns `ticket-info` "
        "metadata only — the real session cookie is set HttpOnly by the PDM "
        "frontend, not retrievable from the JSON response. Token auth is the "
        "only programmatic write path (covered by SC-42)."
    )
)
def test_ticket_write_without_csrf_is_rejected(creds: Credentials) -> None:
    pass
