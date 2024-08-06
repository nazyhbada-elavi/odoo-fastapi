import json
import logging

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas import PartnerList, PartnerID, PartnerIDList, OnePartnerID

router = APIRouter(tags=["Partners"])
_logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.put("/partners", response_model=PartnerIDList | OnePartnerID)
async def edit_partners(partners: PartnerList, env: Annotated[Environment, Depends(odoo_env)],
                        token: Annotated[str, Depends(oauth2_scheme)]) -> PartnerIDList | OnePartnerID:
    token_exists = env['auth.api.key'].search_count([('key', '=', token)])
    if not token_exists:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    _logger.info("edit_partners: input data => \n%s", partners.model_dump_json())

    partners = partners.data

    if not partners:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty data")

    found_partners = []
    not_found_partners = []
    for line in partners:

        partner_id = env['res.partner'].search([('email', '=', line.email)], limit=1)
        if not partner_id:
            partner_id = env['res.partner'].create({
                'email': line.email,
                'name': line.name,
                'synced_from_flyer': True
            })
            not_found_partners.append(line.model_dump())

        res = partner_id.export_data(['id'])
        complete_name = res.get('datas')[0][0]

        partner_id.write({'flyer_id': line.flyer_id})
        partner = PartnerID(flyer_id=line.flyer_id, odoo_id=complete_name)
        found_partners.append(partner)

    if not_found_partners:
        _logger.info("edit_partners: not_found_partners => \n%s", json.dumps(not_found_partners, indent=2))

    if len(found_partners) == 1:
        return OnePartnerID(result=found_partners[0].odoo_id)
    return PartnerIDList(result=found_partners)
