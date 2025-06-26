from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        help="Indicated which contract line that has taken the quantity from this account.move.line and added it to a new invoice",
    )
