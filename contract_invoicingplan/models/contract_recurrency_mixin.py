
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ContractRecurrencyMixin(models.AbstractModel):
    _inherit = "contract.recurrency.mixin"

    recurring_next_date = fields.Date(string="Next Date")