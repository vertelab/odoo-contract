import logging

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class AgreementContract(models.Model):
    _description = "Agreement Contract"
    _inherit = 'agreement'
    _inherits = {
            }

    contract_id = fields.Many2one(
            'contract.contract',
            string="Contract",
            required=False,
            default=None,
            )

    @api.depends("contract_id")
    def _yearly_cost(self):
        self.yearly_cost = 3.14159265

    yearly_cost = fields.Float(
            string="Yearly cost",
            compute=_yearly_cost,
            )
