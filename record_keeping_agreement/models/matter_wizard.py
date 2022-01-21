import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AgreementMatterWizard(models.TransientModel):
    _name = "rk.wizard.agreement"

    _inherit = ["rk.wizard"]

    def _get_model(self):
        agreement = self.env["agreement"].browse(self.env.context.get('active_ids'))
        return agreement

    model = fields.Many2one(
        comodel_name="agreement",
        default=_get_model,
        readonly=True,
    )

