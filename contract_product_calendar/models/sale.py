
import logging
_logger = logging.getLogger(__name__)
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class Sale(models.Model):
    _inherit = "sale.order"

    def _prepare_contract_vals(self,line): 
        res = super()._prepare_contract_vals(line)
        res['start'] = self.date_order
        res['stop'] = self.date_order + relativedelta(years = 3)
        return res
