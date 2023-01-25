import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"
    
    @api.onchange('recurring_next_date','invoice_all_of_last_month','recurring_invoicing_type','recurring_rule_type','recurring_interval')
    def _find_hours_date(self):
        
        for rec in self:
            if rec.recurring_invoicing_type == "post-paid":
                rec.find_hours_date_start = rec.recurring_next_date - relativedelta(months=rec.recurring_interval) ###Not done here!!!!!!!!! Need some way
                rec.find_hours_date_end = rec.recurring_next_date
            elif rec.recurring_invoicing_type == "pre-paid":
                rec.find_hours_date_start = rec.recurring_next_date
                rec.find_hours_date_end = rec.next_period_date_end
            
            if rec.invoice_all_of_last_month:
                if rec.recurring_rule_type != "monthly":
                    raise UserError(_("""I have not implemented the logic for other recurring types then Monthly when combined with Invoice the entire month feature.
                    \nKindly turn of Invoice the entire of you want to use another recurring type.
                    """))
                rec.find_hours_date_start = rec.find_hours_date_start.replace(day=1) 
                rec.find_hours_date_end = rec.find_hours_date_start + relativedelta(months=rec.recurring_interval)
                rec.find_hours_date_end = rec.find_hours_date_end - timedelta(days=1)
    
    find_hours_date_start = fields.Date(
        string="Timesheet start date",
        compute="_find_hours_date",
    )
    find_hours_date_end = fields.Date(
        string="Timesheet end date",
        compute="_find_hours_date",
    )

  
    invoice_all_of_last_month = fields.Boolean(default=True, String="Invoice the entire month", help="If this is turned on we will create invoices and grab time reports for the entirety of last month, so for example we have the next invoice date 2023-02-12 than we will create an invoice and use the hours for the entirety of january.")

    def _get_time_amount_domain(self,line,context,user,period_first_date,period_last_date):
        return [
            # ~ ('account_id', '=', line.analytic_account_id.id),
            ('product_id', '=', False),
            ('project_id', '=', self.project_id.id),
            ('date', '>=', self.find_hours_date_start),
            ('date', '<=', self.find_hours_date_end),
        ]
    def _get_time_amount_fields(self,line,context,user,period_first_date,period_last_date):
        return ['unit_amount']
  
    def _get_time_amount(self,line,context,user,period_first_date,period_last_date):
        fields = self._get_time_amount_fields(line,context,user,period_first_date,period_last_date)
        res = self.env['account.analytic.line'].read_group(
            self._get_time_amount_domain(line,context,user,period_first_date,period_last_date),
            fields = fields,
            groupby=[])
        if res[0]['unit_amount'] == None:
            return 0
        return res[0]['unit_amount']
        # ~ if len(res) == 1:
            # ~ return 0
        # ~ return res.get(fields[0],0.0)



#TODO: if there is a contract in the making and a line with this product then update ????

