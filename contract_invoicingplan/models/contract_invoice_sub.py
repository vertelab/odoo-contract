from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ContractInvoiceSub(models.Model):
    _name = 'contract.invoice.stub'
    _description = 'Contract Invoice Stub'
    _order = "date asc"

    date = fields.Date(string="Date")
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

    def _get_next_recurring_date(self):
        next_contract_invoice_stub = self.env['contract.invoice.stub'].search([
            ('contract_id', '=', self.contract_id.id),
            ('account_move_id', '=', False),
        ], limit=1)
        return next_contract_invoice_stub

    def action_create_move(self):
        invoice = self.contract_id.recurring_create_invoice()
        self.write({
            'account_move_id': invoice.id,
        })
        self.contract_id.write({
            'recurring_next_date': self._get_next_recurring_date().date if self._get_next_recurring_date() else self.date
        })

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
        ])
        for contract_invoice_stub_id in contract_invoice_stub_ids:
            invoice_stub_id = contract_invoice_stub_id.contract_id.recurring_create_invoice()
            contract_invoice_stub_id.write({
                'account_move_id': invoice_stub_id.id
            })