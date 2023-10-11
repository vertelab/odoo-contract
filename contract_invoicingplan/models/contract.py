from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"

    invoice_stub_ids = fields.One2many('contract.invoice.stub', 'contract_id', string="Invoice Stub")

    @api.depends('invoice_stub_ids')
    def _set_uninvoiced_stubs(self):
        for rec in self:
            rec.uninvoiced_stubs = any(
                item.date < fields.Date.today() and not item.account_move_id
                for item in rec.invoice_stub_ids if item.date
            )

    uninvoiced_stubs = fields.Boolean(string="UnInvoiced Stubs", default=False, compute=_set_uninvoiced_stubs,
                                      store=True)

    @api.depends('invoice_stub_ids')
    def _compute_contract_invoice_sub_count(self):
        for rec in self:
            rec.contract_invoice_sub_count = len(rec.invoice_stub_ids)

    contract_invoice_sub_count = fields.Integer(string="Invoice Sub",
                                                compute=_compute_contract_invoice_sub_count, store=True)

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
        last_invoicing_date = self.date_start
        if self.invoice_stub_ids:
            last_invoicing_date = self.invoice_stub_ids.sorted(key=lambda r: r.date)[-1].mapped('date')[
                                      0] + relativedelta(months=1)

        date_end = self.date_end if self.date_end else last_invoicing_date + relativedelta(months=11)
        while invoicing_date <= date_end:
            _logger.warning(f"Running while with invoicing date: {invoicing_date}")
            contract_invoice_stub_id = self.env['contract.invoice.stub'].search([
                ('contract_id', '=', self.id),
                ('date', '=', invoicing_date),
            ])

            if not contract_invoice_stub_id:
                self.env['contract.invoice.stub'].create({
                    'amount': self._compute_contract_lines(),
                    'date': invoicing_date,
                    'period_date_end': self.get_next_period_date_end(invoicing_date,
                                                                     self.recurring_rule_type,
                                                                     self.recurring_interval,
                                                                     max_date_end=self.date_end),
                    'contract_id': self.id
                })
            elif contract_invoice_stub_id and not contract_invoice_stub_id.account_move_id:
                contract_invoice_stub_id.write({'amount': self._compute_contract_lines()})

            _logger.warning(f"{invoicing_date + relativedelta(days=1)=}")
            _logger.warning(f"{self.recurring_rule_type=}")
            _logger.warning(f"{self.recurring_interval=}")
            _logger.warning(f"{self.date_end=}")
            invoicing_date = self.get_next_period_date_end(invoicing_date + relativedelta(days=1),
                                                           self.recurring_rule_type,
                                                           self.recurring_interval,
                                                           max_date_end=self.date_end)

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

    def _set_contract_line_next_period_date(self, sub):
        self.next_period_date_start = sub.date
        self.next_period_date_end = sub.period_date_end
        for line in self.contract_line_ids:
            line.recurring_next_date = sub.date
            line.next_period_date_start = sub.date
            line.next_period_date_end = sub.period_date_end

    # ~ def get_strftime_start(self, format_list):
    # ~ return " ".join([self.next_period_date_start.strftime(f) for f in format_list] )

    # ~ def get_strftime_end(self, format_list):
    # ~ return " ".join([self.next_period_date_end.strftime(f) for f in format_list] )
