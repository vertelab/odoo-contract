from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ContractLine(models.Model):
    _inherit = "contract.line"

    active_stub_start_date = fields.Date(string="Active Stub Start Date", related='contract_id.active_stub_start_date')

    active_stub_end_date = fields.Date(string="Active Stub End Date", related='contract_id.active_stub_end_date')

    def get_strftime_stub_start(self, format_list):
        return " ".join([self.active_stub_start_date.strftime(f) for f in format_list])

    def get_strftime_stub_end(self, format_list):
        return " ".join([self.active_stub_end_date.strftime(f) for f in format_list])
    
    def _prepare_invoice_line(self):
        invoice_line_vals = super()._prepare_invoice_line()
        if self.qty_type == 'fixed/percentage':
            invoice_sub_line = self.contract_id.invoice_stub_ids.filtered(
                lambda sub: sub.date == self.active_stub_start_date
            )
            invoice_line_vals['price_unit'] = invoice_sub_line.amount
        return invoice_line_vals


class Contract(models.Model):
    _inherit = "contract.contract"

    invoice_stub_ids = fields.One2many('contract.invoice.stub', 'contract_id', string="Invoice Stub")

    active_stub_start_date = fields.Date(string="Active Stub Start Date")

    active_stub_end_date = fields.Date(string="Active Stub End Date")

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
            'view_mode': 'list',
            'res_model': 'contract.invoice.stub',
            'target': 'current',
            'domain': [('contract_id', '=', self.id)],
            'views': [[False, 'list']],
        }

    def _get_starting_date(self):
        """Get the initial invoicing date"""
        if self.invoice_stub_ids:
            last_date = self.invoice_stub_ids.sorted(key=lambda r: r.date)[-1].mapped('date')[0]
            return last_date + relativedelta(months=1)
        return self.date_start

    def _get_end_date(self, start_date):
        """Get the contract end date"""
        return self.date_end if self.date_end else start_date + relativedelta(months=11)

    def compute_contract(self):
        """Main method to compute contract invoice stubs"""
        self._clear_uninvoiced_lines()

        invoicing_date = self._get_starting_date()
        date_end = self._get_end_date(invoicing_date)

        while invoicing_date and (invoicing_date <= date_end):
            _logger.warning(f"Running while with invoicing date: {invoicing_date}")

            self._process_stub_for_date(invoicing_date)
            invoicing_date = self._get_next_invoicing_date(invoicing_date)

    def _process_stub_for_date(self, invoicing_date):
        """Create or update stub for given date"""
        existing_stub = self.env['contract.invoice.stub'].search([
            ('contract_id', '=', self.id),
            ('date', '=', invoicing_date),
        ])

        stub_amount = self._compute_contract_lines()

        if not existing_stub:
            self.env['contract.invoice.stub'].create({
                'amount': stub_amount,
                'date': invoicing_date,
                'period_date_end': self.get_next_period_date_end(invoicing_date,
                                                                 self.recurring_rule_type,
                                                                 self.recurring_interval,
                                                                 max_date_end=self.date_end),
                'contract_id': self.id
            })
        elif not existing_stub.account_move_id:
            existing_stub.write({'amount': stub_amount})

    def _get_next_invoicing_date(self, current_date):
        """Calculate next invoicing date - override this to fix the duplicate issue"""
        if self.recurring_rule_type == 'monthly':
            return current_date + relativedelta(months=self.recurring_interval)
        elif self.recurring_rule_type == 'yearly':
            return current_date + relativedelta(years=self.recurring_interval)
        else:
            # Fallback to original logic
            return self.get_next_period_date_end(current_date + relativedelta(days=1),
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

    def unlink(self):
        for record in self:
            stub_ids = record.invoice_stub_ids
            invoiced_stubs = stub_ids.filtered(
                lambda stub_line:
                stub_line.account_move_id and stub_line.account_move_id.state not in ['draft', 'cancel']
            )
            if invoiced_stubs:
                raise ValidationError(_("One of the stubs has a posted invoice."))
            stub_ids.unlink()
        return super().unlink()
