import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"
  
    def _get_time_amount_domain(self,line,context,user,invoice,period_first_date,period_last_date):
        return [
            ('account_id', '=', line.analytic_account_id.id),
            ('product_id', '=', False),
            ('project_id', '!=', False),
            ('date', '&gt;=', period_first_date),
            ('date', '&lt;=', period_last_date),
        ]
    def _get_time_amount_fields(self,line,context,user,invoice,period_first_date,period_last_date):
        return ['unit_amount']
  
    def _get_time_amount(self,line,context,user,invoice,period_first_date,period_last_date):
        fields = self._get_time_amount_fields(self,line,context,user,invoice,period_first_date,period_last_date)
        res = self.env['account.analytic.line'].read_group(
            self._get_time_amount_domain(self,line,context,user,invoice,period_first_date,period_last_date),
            fields = fields,
            groupby=[])
        res['unit_amount'] = res[fields[0]]
        return res
        
     
#TODO: if there is a contract in the making and a line with this product then update ????

