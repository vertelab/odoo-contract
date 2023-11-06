from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class ContractInvoiceSub(models.Model):
    _name = 'contract.invoice.stub'
    _description = 'Contract Invoice Stub'
    _order = "date asc"

    # TODO: Rename date to period_date_start
    date = fields.Date(string="Period Date Start")
    period_date_end = fields.Date(string="Period Date End")
    amount = fields.Float(string="Amount")
    contract_id = fields.Many2one('contract.contract', string="Contract")
    has_move = fields.Boolean(string='Has Move', default=False, compute='_check_contract_invoice_move')
    account_move_id = fields.Many2one('account.move', string="Account")

    def action_view_move(self):
        view_id = self.env.ref('account.view_move_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import your first bill'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'target': 'current',
            'res_id': self.account_move_id.id,
            'views': [[view_id, 'form']],
        }

    def action_delete_move(self):
        self.account_move_id.unlink()
        self.contract_id._set_uninvoiced_stubs()

    def _get_next_recurring_date(self):
        next_contract_invoice_stub = self.env['contract.invoice.stub'].search([
            ('contract_id', '=', self.contract_id.id),
            ('account_move_id', '=', False),
        ], limit=1)
        return next_contract_invoice_stub

    def action_create_move(self):
        self.amount = self.contract_id._compute_contract_lines()

        self.contract_id._set_contract_line_next_period_date(self)
        invoices = self.contract_id._recurring_create_invoice(self.date)
        for invoice in invoices:
            invoice.message_post(
                body=_(
                    "Contract manually invoiced by stubs: "
                    '<a href="#" data-oe-model="%s" data-oe-id="%s">Invoice'
                    "</a>"
                )
                     % (invoice._name, invoice.id),
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            )
        self.write({
            'account_move_id': invoice.id,
        })

        self.account_move_id.write({
            'contract_stub_id': self.id,
            'contract_id': self.contract_id.id,
        })

        self.contract_id.write({
            'recurring_next_date': self._get_next_recurring_date().date if self._get_next_recurring_date() else self.date
        })
        self.contract_id._set_uninvoiced_stubs()

    @api.depends('account_move_id')
    def _check_contract_invoice_move(self):
        for rec in self:
            if rec.account_move_id:
                rec.has_move = True
            else:
                rec.has_move = False

    def unlink(self):
        if self.account_move_id:
            raise ValidationError("You cannot delete this record because an account move is linked")
        return super().unlink()

    def _cron_action_create_move(self):
        contract_invoice_stub_ids = self.env['contract.invoice.stub'].search([
            ('date', '=', fields.Date.today()),
            ('account_move_id', '=', False),
            ('contract_id.active', '=', True)
        ])
        for contract_invoice_stub_id in contract_invoice_stub_ids:
            contract_invoice_stub_id.contract_id._set_contract_line_next_period_date(contract_invoice_stub_id)
            invoice = contract_invoice_stub_id.contract_id._recurring_create_invoice(contract_invoice_stub_id.date)
            contract_invoice_stub_id.contract_id.message_post(
                body=_(
                    "Contract automaticly invoiced by cron: "
                    '<a href="#" data-oe-model="%s" data-oe-id="%s">Invoice'
                    "</a>"
                )
                     % (invoice._name, invoice.id),
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            )

            contract_invoice_stub_id.write({
                'account_move_id': invoice.id,
                'amount': contract_invoice_stub_id.contract_id._compute_contract_lines()
            })
            contract_invoice_stub_id.contract_id.write({
                'recurring_next_date': contract_invoice_stub_id._get_next_recurring_date().date if contract_invoice_stub_id._get_next_recurring_date() else contract_invoice_stub_id.date
            })
