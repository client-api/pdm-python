"""SC-41 / SC-42 — error-path correctness."""
from __future__ import annotations

import pytest

from clientapi_pdm import Configuration, Pdm
from clientapi_pdm.exceptions import ApiException
from clientapi_pdm.models.access_users_create_token_request import (
    AccessUsersCreateTokenRequest,
)
from clientapi_pdm.models.access_users_create_users_request import (
    AccessUsersCreateUsersRequest,
)
from e2e.helpers.credentials import Credentials


def test_invalid_password_length_rejected(pdm: Pdm) -> None:
    """SC-41 — invalid input (password too short) is caught client- or server-side."""
    with pytest.raises(Exception) as excinfo:
        pdm.accessUsers.create_users(
            AccessUsersCreateUsersRequest(userid="e2e-tooshort@pdm", password="abc")
        )
    assert excinfo.type.__name__ in {"ValidationError", "BadRequestException", "ApiException"}, excinfo.value


def test_privsep_token_without_acl_is_forbidden(pdm: Pdm, creds: Credentials) -> None:
    """SC-42 — token with no ACL receives 401/403 on writes."""
    user_id = "e2e-noacl@pdm"
    pdm.accessUsers.create_users(
        AccessUsersCreateUsersRequest(
            userid=user_id, password="long-enough-password-1234"
        )
    )
    try:
        token_response = pdm.accessUsers.create_token(
            userid=user_id,
            token_name="noacl",
            access_users_create_token_request=AccessUsersCreateTokenRequest(),
        )
        tokenid = token_response.data.tokenid
        value = token_response.data.value
        header_value = f"PDMAPIToken={tokenid}:{value}"

        cfg = Configuration(host=f"{creds.url}/api2/json")
        cfg.verify_ssl = not creds.insecure
        cfg.api_key["PDMApiToken"] = header_value
        client = Pdm(cfg)

        with pytest.raises(ApiException) as excinfo:
            client.accessUsers.create_users(
                AccessUsersCreateUsersRequest(
                    userid="e2e-blocked2@pdm",
                    password="long-enough-password-1234",
                )
            )
        assert excinfo.value.status in (401, 403), excinfo.value
    finally:
        try:
            pdm.accessUsers.delete_users(userid=user_id)
        except ApiException:
            pass
