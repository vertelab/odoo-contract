import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"
    
    
    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref)
        
        for move in moves:
            for line in move.line_ids:
                for time_report_line in line.analytic_line_ids_time_report:
                    time_report_line.move_id = line.id
                    move.write({"timesheet_ids":[(4, time_report_line.id, 0)]})

        return moves
    
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

    def _get_time_amount_domain(self):
        return [
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
            self._get_time_amount_domain(),
            fields = fields,
            groupby=[])
        if res[0]['unit_amount'] == None:
            return 0
        return res[0]['unit_amount']
        # ~ if len(res) == 1:
            # ~ return 0
        # ~ return res.get(fields[0],0.0)
        
    
        
class ContractLine(models.Model):
    _inherit = "contract.line"

    def _prepare_invoice_line(self, move_form):
        ## Need some smart way of connecting analytic lines with the invoice line.
        ## What I opted for is to reuse these varable formulas but look for a new variable called time_report_lines_domain.
        ## This way we can define in the formulas when it is relevant to connect an invoice line to account.analytic.lines.
        ## Potential issues is that the quantity won't mirror the amount of account.analytic.lines 
        ## depending on the domain we return.
                
        period_first_date, period_last_date, invoice_date = self._get_period_to_invoice(
            self.last_date_invoiced, self.recurring_next_date
        )
        quantity = self._get_quantity_to_invoice(period_first_date, period_last_date, invoice_date)
        _logger.warning(f"{quantity=}, {period_first_date=}, {period_last_date=}, {invoice_date=}")
        
        vals = super()._prepare_invoice_line(move_form)
        if vals and self.qty_type == "variable":
            eval_context = {
                "env": self.env,
                "context": self.env.context,
                "user": self.env.user,
                "line": self,
                "quantity": quantity,
                "period_first_date": period_first_date,
                "period_last_date": period_last_date,
                "invoice_date": invoice_date,
                "contract": self.contract_id,
            }
            safe_eval(
                self.qty_formula_id.code.strip(),
                eval_context,
                mode="exec",
                nocopy=True,
            )  # nocopy for returning result
            time_report_lines_domain = eval_context.get("time_report_lines_domain", False)
            _logger.warning(f"{time_report_lines_domain=}")
            if time_report_lines_domain:
                vals['analytic_line_ids_time_report'] = self.env["account.analytic.line"].search(time_report_lines_domain)
        _logger.warning(f"{vals=}")
        return vals
        
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    analytic_line_ids_time_report = fields.One2many('account.analytic.line', 'move_id_time_report', string='Analytic lines Timereports')

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    move_id_time_report = fields.Many2one('account.move.line', string='Journal Item', ondelete='cascade', index=True, check_company=True)


#TODO: if there is a contract in the making and a line with this product then update ????


