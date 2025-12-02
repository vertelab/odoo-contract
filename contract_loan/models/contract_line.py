from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError, UserError


class ContractLine(models.Model):
    _inherit = "contract.line"

    loan_id = fields.Many2one('account.loan')

    def _prepare_invoice_line(self):
        invoice_line_vals = super()._prepare_invoice_line()

        if not self.loan_id:
            return invoice_line_vals

        current_loan_line = self.env['account.loan.line'].search([
            ('loan_id', '=', self.loan_id.id),
            ('date', '>=', self.contract_id.active_stub_start_date),
            ('date', '<=', self.contract_id.active_stub_end_date)
        ])

        if not current_loan_line:
            return invoice_line_vals

        # Get invoice line values from the loan line (returns a list)
        # If super() already returned a list, use it; otherwise fetch fresh
        if isinstance(invoice_line_vals, list):
            loan_line_vals_list = invoice_line_vals
            base_sequence = 10  # Default since we don't have original
        else:
            loan_line_vals_list = current_loan_line._invoice_line_vals()
            base_sequence = invoice_line_vals.get('sequence', 10)

        # Calculate total amount (principal + interest)
        total_amount = sum(
            line_vals.get('price_unit', 0.0) * line_vals.get('quantity', 1.0)
            for line_vals in loan_line_vals_list
        )

        # Build invoice lines: section with total + loan lines
        lines = self._description(base_sequence, total_amount)

        # Add all loan lines (principal and interest)
        for idx, loan_line_vals in enumerate(loan_line_vals_list):
            # Keep them tightly grouped with base_sequence + small increments
            loan_line_vals['sequence'] = base_sequence + 0.001 + (idx * 0.001)
            lines.append(loan_line_vals)
        return lines

    def _description(self, base_sequence, total_amount):
        lines = [{
            'display_type': 'line_section',
            'name': _('Loan Details for: %s - Total: %.2f kr') % (
                self.loan_id.name, total_amount
            ),
            'sequence': base_sequence,
        }]
        return lines
