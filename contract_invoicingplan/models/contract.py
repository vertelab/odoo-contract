from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class Contract(models.Model):
    _inherit = "contract.contract"

    invoice_stub_ids = fields.One2many('contract.invoice.stub', 'contract_id', string="Invoice Stub")

    @api.depends('invoice_stub_ids')
    def _compute_contract_invoice_sub_count(self):
        for rec in self:
            rec.contract_invoice_sub_count = len(rec.invoice_stub_ids)

    contract_invoice_sub_count = fields.Integer(string="Invoice Sub", compute=_compute_contract_invoice_sub_count)

    def action_show_contract_invoice_stub(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contract Invoice Stubs'),
            'view_mode': 'tree',
            'res_model': 'contract.invoice.stub',
            'target': 'current',
            'domain': [('contract_id', '=', self.id)],
            'views': [[False, 'tree']],
        }

    def compute_contract(self):
        self._clear_uninvoiced_lines()
        invoicing_date = self.date_start
        date_end = self.date_end if self.date_end else self.date_start + relativedelta(months=1)
        while invoicing_date <= date_end:
            contract_invoice_stub_id = self.env['contract.invoice.stub'].search([
                ('contract_id', '=', self.id),
                ('date', '=', invoicing_date),
            ])

            if not contract_invoice_stub_id:
                self.env['contract.invoice.stub'].create({
                    'amount': self._compute_contract_lines(),
                    'date': invoicing_date,
                    'contract_id': self.id
                })
            elif contract_invoice_stub_id and not contract_invoice_stub_id.account_move_id:
                contract_invoice_stub_id.write({'amount': self._compute_contract_lines()})

            invoicing_date += relativedelta(months=1)

    def _compute_contract_lines(self):
        total_price_subtotal = []
        for line in self.contract_line_fixed_ids:
            dates = line._get_period_to_invoice(
                line.last_date_invoiced, line.recurring_next_date
            )
            total_price_subtotal.append(line._get_quantity_to_invoice(*dates) * line.price_unit)

        return sum(total_price_subtotal)

    def _clear_uninvoiced_lines(self):
        lines = self.invoice_stub_ids.filtered(lambda line: not line.account_move_id)
        lines.unlink()