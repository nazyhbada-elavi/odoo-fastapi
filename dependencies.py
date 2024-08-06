from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader, OAuth2PasswordRequestForm
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.base.models.res_users import Users
from odoo.addons.base.models.res_partner import Partner
from starlette import status

from odoo.api import Environment


def authenticated_partner(
        env: Annotated[Environment, Depends(odoo_env)],
        security: OAuth2PasswordRequestForm,
) -> Users:
    user = env["res.users"].sudo().search(
        [("login", "=", security.username)], limit=1
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    #### copied from _check_credentials
    env.cr.execute(
        "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
        [user.id]
    )
    [hashed] = env.cr.fetchone()
    valid, replacement = user._crypt_context() \
        .verify_and_update(security.password, hashed)
    if replacement is not None:
        user._set_encrypted_password(user.id, replacement)
    ####

    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


def api_key_auth(
        user: Annotated[str, Depends(APIKeyHeader(name="X-login", scheme_name="Login"))],
        api_key: Annotated[str, Depends(APIKeyHeader(name="X-api-key"))],
        env: Annotated[Environment, Depends(odoo_env)],
) -> Partner:
    user_id = env["res.users"].sudo().search(
        [("login", "=", user)], limit=1
    )
    if not user_id.partner_id.api_key:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="API Key is not set"
        )
    if user_id.partner_id.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect API Key"
        )
    return env.user.partner_id
