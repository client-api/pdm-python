"""Client factories for the two auth modes PDM supports."""
from __future__ import annotations

from typing import TYPE_CHECKING

from clientapi_pdm import Configuration, Pdm

if TYPE_CHECKING:
    from e2e.helpers.credentials import Credentials


def token_client(creds: "Credentials") -> Pdm:
    cfg = Configuration(host=f"{creds.url}/api2/json")
    cfg.verify_ssl = not creds.insecure
    cfg.api_key["PDMApiToken"] = creds.token_header_value
    return Pdm(cfg)


def ticket_client(
    creds: "Credentials",
    *,
    ticket: str,
    csrf: str | None = None,
) -> Pdm:
    cfg = Configuration(host=f"{creds.url}/api2/json")
    cfg.verify_ssl = not creds.insecure
    cfg.api_key["PDMAuthCookie"] = ticket
    if csrf is not None:
        cfg.api_key["CSRFPreventionToken"] = csrf
    return Pdm(cfg)


def issue_ticket(creds: "Credentials", *, password: str | None = None) -> Pdm:
    """Probe the PDM ticket endpoint.

    Returns an unconfigured Pdm client on success (PDM's `/access/ticket`
    yields `ticket-info` metadata rather than a usable session token, so this
    helper exists for the SC-11 wrong-password probe — it'll raise
    ApiException(401) on bad credentials, matching the test's expectation.
    """
    from clientapi_pdm.models.access_ticket_create_ticket_request import (
        AccessTicketCreateTicketRequest,
    )

    anon = Configuration(host=f"{creds.url}/api2/json")
    anon.verify_ssl = not creds.insecure
    bootstrap = Pdm(anon)

    bootstrap.accessTicket.create_ticket(
        AccessTicketCreateTicketRequest(
            username=creds.user,
            password=password if password is not None else creds.password,
        )
    )
    return bootstrap
