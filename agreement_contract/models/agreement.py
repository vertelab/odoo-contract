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

