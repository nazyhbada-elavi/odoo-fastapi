from odoo import fields, models
from ..routers import router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("flyer", "Flyer Endpoint")], ondelete={"flyer": "cascade"}
    )

    def _get_fastapi_routers(self):
        if self.app == "flyer":
            return [router]
        return super()._get_fastapi_routers()
