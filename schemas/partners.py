from pydantic import BaseModel, Field
from typing import Optional


class Partner(BaseModel):
    flyer_id: int = Field(gt=0)
    name: str
    email: str


class PartnerList(BaseModel):
    data: list[Partner]


class PartnerID(BaseModel):
    flyer_id: int
    odoo_id: str


class PartnerIDList(BaseModel):
    result: list[PartnerID]


class OnePartnerID(BaseModel):
    result: str
