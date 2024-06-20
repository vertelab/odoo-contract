import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval
from collections import defaultdict

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"

    def _recurring_create_invoice(self, date_ref=False):
        moves = super()._recurring_create_invoice(date_ref)

        for move in moves:
            for line in move.line_ids:
                for time_report_line in line.analytic_line_ids_time_report:
                    time_report_line.timesheet_invoice_id = move.id

        return moves

    @api.onchange('recurring_next_date', 'invoice_all_of_last_month', 'recurring_invoicing_type', 'recurring_rule_type',
                  'recurring_interval')
    def _find_hours_date(self):

        for rec in self:
            if rec.recurring_invoicing_type == "post-paid":
                rec.find_hours_date_start = rec.recurring_next_date - relativedelta(
                    months=rec.recurring_interval)  ###Not done here!!!!!!!!! Need some way
                rec.find_hours_date_end = rec.recurring_next_date
            elif rec.recurring_invoicing_type == "pre-paid":
                rec.find_hours_date_start = rec.recurring_next_date
                rec.find_hours_date_end = rec.next_period_date_end

            if rec.invoice_all_of_last_month:
                #if rec.recurring_rule_type != "monthly":
                #    raise UserError(_("""I have not implemented the logic for other recurring types then Monthly when 
                #    combined with Invoice the entire month feature.
                #    \nKindly turn of Invoice the entire of you want to use another recurring type.
                #    """))
                if rec.find_hours_date_start:
                    rec.find_hours_date_start = rec.find_hours_date_start.replace(day=1)
                    rec.find_hours_date_end = (rec.find_hours_date_start + relativedelta(months=rec.recurring_interval)) - timedelta(days=1)
                else:
                    rec.find_hours_date_start = False
                    rec.find_hours_date_end = False

    find_hours_date_start = fields.Date(
        string="Timesheet start date",
        compute="_find_hours_date",
    )
    find_hours_date_end = fields.Date(
        string="Timesheet end date",
        compute="_find_hours_date",
    )

    invoice_all_of_last_month = fields.Boolean(default=True, String="Invoice the entire month",
                                               help="If this is turned on we will create invoices and grab time "
                                                    "reports for the entirety of last month, so for example we have "
                                                    "the next invoice date 2023-02-12 than we will create an invoice "
                                                    "and use the hours for the entirety of january.")

    def _get_time_amount_domain(self, line):
        return [
            ('product_id', '=', False),
            ('project_id', '=', line.project_id.id),
            #('date', '>=', self.find_hours_date_start),
            ('date', '<=', self.find_hours_date_end),
            ('timesheet_invoice_id', '=', False),
        ]

    def _get_time_amount_fields(self, line, context, user, period_first_date, period_last_date):
        return ['unit_amount']

    def _get_time_amount(self, line, context, user, period_first_date, period_last_date):
        _logger.warning(f"{line=},{context=},{user=},{period_first_date=},{period_last_date=}")
        fields = self._get_time_amount_fields(line, context, user, period_first_date, period_last_date)
        res = self.env['account.analytic.line'].read_group(
            self._get_time_amount_domain(line),
            fields=fields,
            groupby=[])
        if res[0]['unit_amount'] == None:
            return 0
        return res[0]['unit_amount']


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
                vals['analytic_line_ids_time_report'] = self.env["account.analytic.line"].search(
                    time_report_lines_domain)
        _logger.warning(f"{vals=}")

        return vals


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    analytic_line_ids_time_report = fields.One2many('account.analytic.line', 'move_id_time_report',
                                                    string='Analytic lines Timereports')

    def unlink(self):
        """
                                TODO YOU WATCHMAN:
        this function was override from, odoo.addons.sale_timesheet.models.account_move,
        it initially works with sale order, but with the introduction on contract, we need to observe it still works,
        both with contract and with sales.
        """
        move_line_read_group = self.env['account.move.line'].search_read([
            ('move_id.move_type', '=', 'out_invoice'),
            ('move_id.state', '=', 'draft'),
            ('sale_line_ids.product_id.invoice_policy', '=', 'delivery'),
            ('sale_line_ids.product_id.service_type', '=', 'timesheet'),
            ('id', 'in', self.ids)],
            ['move_id', 'sale_line_ids', 'contract_line_ids'])

        # moves for sale order
        sale_line_ids_per_move = defaultdict(lambda: self.env['sale.order.line'])

        # moves for contracts
        contract_line_ids_per_move = defaultdict(lambda: self.env['contract.line'])

        for move_line in move_line_read_group:
            # moves for sale order line
            sale_line_ids_per_move[move_line['move_id'][0]] += self.env['sale.order.line'].browse(
                move_line['sale_line_ids']
            )

            # moves for contract line
            contract_line_ids_per_move[move_line['move_id'][0]] += self.env['contract.line'].browse(
                move_line['contract_line_ids']
            )

        timesheet_read_group = self.sudo().env['account.analytic.line'].read_group([
            ('timesheet_invoice_id.move_type', '=', 'out_invoice'),
            ('timesheet_invoice_id.state', '=', 'draft'),
            ('timesheet_invoice_id', 'in', self.move_id.ids)],
            ['timesheet_invoice_id', 'so_line', 'ids:array_agg(id)'],
            ['timesheet_invoice_id', 'so_line', 'contract_line_id'],
            lazy=False)

        timesheet_ids = []
        for timesheet in timesheet_read_group:
            move_id = timesheet['timesheet_invoice_id'][0]

            # timesheet for sale order
            if timesheet['so_line'] and timesheet['so_line'][0] in sale_line_ids_per_move[move_id].ids:
                timesheet_ids += timesheet['ids']

            # timesheet for contract
            if timesheet['contract_line_id'] and timesheet['contract_line_id'][0] in contract_line_ids_per_move[
                move_id].ids:
                timesheet_ids += timesheet['ids']

        self.sudo().env['account.analytic.line'].browse(timesheet_ids).write({'timesheet_invoice_id': False})
        return super(AccountMoveLine, self).unlink()

class AccountMove(models.Model):
    _inherit = "account.move"
    def _reset_invoice(self):
        AccountMoveLine = self.env['account.move.line']
        excluded_move_ids = []

        if self._context.get('suspense_moves_mode'):
            excluded_move_ids = AccountMoveLine.search(
                AccountMoveLine._get_suspense_moves_domain() + [('move_id', 'in', self.ids)]).mapped('move_id').ids

        for move in self:
            if move in move.line_ids.mapped('full_reconcile_id.exchange_move_id'):
                raise UserError(_('You cannot reset to draft an exchange difference journal entry.'))
            if move.tax_cash_basis_rec_id:
                raise UserError(_('You cannot reset to draft a tax cash basis journal entry.'))
            if move.restrict_mode_hash_table and move.state == 'posted' and move.id not in excluded_move_ids:
                raise UserError(_('You cannot modify a posted entry of this journal because it is in strict mode.'))

        self.mapped('line_ids').remove_move_reconcile()
        self.write({'state': 'draft', 'is_move_sent': False})
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    move_id_time_report = fields.Many2one('account.move.line', string='Journal Item', ondelete='cascade', index=True,
                                          check_company=True)

# TODO: if there is a contract in the making and a line with this product then update ????
