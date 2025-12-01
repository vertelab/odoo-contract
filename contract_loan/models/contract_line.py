from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError, UserError


class ContractLine(models.Model):
    _inherit = "contract.line"

    loan_id = fields.Many2one('account.loan')

    def _prepare_invoice_line(self):
        invoice_line_vals = super()._prepare_invoice_line()
        if self.loan_id:
           current_loan_line = self.env['account.loan.line'].search([
               ('loan_id', '=', self.loan_id.id),
               ('date', '>=', self.contract_id.active_stub_start_date),
               ('date', '<=', self.contract_id.active_stub_end_date)
           ])
           invoice_line_vals = current_loan_line._invoice_line_vals()
        return invoice_line_vals




