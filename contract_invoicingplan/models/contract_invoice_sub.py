from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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
    recurring_next_date = fields.Date(string="Recurring Next Date",
                                      related='contract_id.recurring_next_date', store=True)
    amount = fields.Float(string="Amount")
    
    def name_get(self):
        res = []
        for stub in self:
            res.append((stub.id,f"[{stub.contract_id.recurring_interval} {stub.contract_id.recurring_rule_type}] {stub.partner_id.name}"))
        return res

    

    @api.depends('contract_id', 'account_move_id', 'account_move_id.state')
    def _compute_amount_forecast(self):
        for rec in self:
            if not rec.account_move_id or rec.account_move_id.state == 'draft' and rec.contract_id:
                previous_contract_stub_id = self.env['contract.invoice.stub'].search([
                    ('account_move_id', '!=', False),
                    ('account_move_id.state', 'not in', ['draft', 'cancel']),
                ], limit=1) - rec
                # previous_contract_stub_id = self.env['contract.invoice.stub'].browse(rec.id - 1)
                if previous_contract_stub_id:
                    rec.compute_amount_forecast = previous_contract_stub_id.account_move_id.amount_untaxed
                else:
                    rec.compute_amount_forecast = rec.amount
            else:
                rec.compute_amount_forecast = rec.amount
            rec.onchange_amount_forecast()

    compute_amount_forecast = fields.Float(string="Amount Forecast", compute=_compute_amount_forecast)

    @api.onchange('compute_amount_forecast')
    def onchange_amount_forecast(self):
        self.amount_forecast = self.compute_amount_forecast

    amount_forecast = fields.Float(string="Amount Forecast", readonly=True)
    contract_id = fields.Many2one(comodel_name='contract.contract', string="Contract")
    contract_template_id = fields.Many2one(comodel_name='contract.template', string="Contract Template",
                                           related='contract_id.contract_template_id', store=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Partner", related='contract_id.partner_id', store=True)
    user_id = fields.Many2one(comodel_name='res.users', string="Responsible", related='contract_id.user_id', store=True)
    has_move = fields.Boolean(string='Has Move', default=False, compute='_check_contract_invoice_move')
    account_move_id = fields.Many2one(comodel_name='account.move', string="Account")

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
        self.contract_id.write({
            'active_stub_start_date': self.date,
            'active_stub_end_date': self.period_date_end,
        })

        self.amount = self.contract_id._compute_contract_lines()

        self.contract_id._set_contract_line_next_period_date(self)
        invoices = self.contract_id._recurring_create_invoice(self.date)
        for invoice in invoices:
            invoice.invoice_date = fields.Date.today()
            invoice.period_id = self.env['account.period'].date2period(invoice.invoice_date)
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
        if self.account_move_id and self.account_move_id.state not in ['draft', 'cancel']:
            raise ValidationError("You cannot delete this record because a posted account move is linked")
        self.account_move_id.with_context(force_delete=True).unlink()
        return super().unlink()

    def _cron_action_create_move(self):
        contract_invoice_stub_ids = self.env['contract.invoice.stub'].search([
            ('date', '=', fields.Date.today()),
            ('account_move_id', '=', False),
            ('contract_id.active', '=', True)
        ])
        for contract_invoice_stub_id in contract_invoice_stub_ids:
            contract_invoice_stub_id.contract_id.write({
                'active_stub_start_date': contract_invoice_stub_id.date,
                'active_stub_end_date': contract_invoice_stub_id.period_date_end,
            })
            contract_invoice_stub_id.contract_id._set_contract_line_next_period_date(contract_invoice_stub_id)
            invoice = contract_invoice_stub_id.contract_id._recurring_create_invoice(contract_invoice_stub_id.date)
            contract_invoice_stub_id.contract_id.message_post(
                body=_(
                    "Contract automatically invoiced by cron: "
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
