import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from odoo.addons.fastapi.dependencies import odoo_env

from odoo.api import Environment
from ..dependencies import authenticated_partner

router = APIRouter(tags=["Auth"])


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                env: Annotated[Environment, Depends(odoo_env)]):
    user = authenticated_partner(env, form_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    api_key_id = env['auth.api.key'].search([('user_id', '=', user.id)], limit=1)
    if not api_key_id:
        api_key_id = env['auth.api.key'].create({
            'name': 'Flyer API Key for user %s' % user.name,
            'key': secrets.token_urlsafe(32),
            'user_id': user.id,
        })
    if (datetime.now() - api_key_id.write_date).days > 1:
        api_key_id.key = secrets.token_urlsafe(32)

    return {"access_token": api_key_id.key, "token_type": "bearer"}
