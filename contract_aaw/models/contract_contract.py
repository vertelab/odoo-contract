from calendar import month
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError, UserError
import logging
import pandas as pd
from datetime import datetime


class Contract(models.Model):
    _inherit = "contract.contract"

    def _prepare_recurring_invoices_values(self, date_ref=False):
        invoices_values = super()._prepare_recurring_invoices_values(date_ref)

        for invoice_vals in invoices_values:
            # Apply the task-based grouping
            invoice_vals['invoice_line_ids'] = self._group_by_task(invoice_vals['invoice_line_ids'])

            # Collect all timesheet_ids and move them to the invoice level
            all_timesheet_ids = []
            for line in invoice_vals.get('invoice_line_ids'):
                if line[2].get('timesheet_ids'):
                    all_timesheet_ids.extend(line[2].pop('timesheet_ids'))

            if all_timesheet_ids:
                invoice_vals['timesheet_ids'] = [(6, 0, all_timesheet_ids)]

        return invoices_values


    def _prepare_invoice(self, date_invoice, journal=None):
        invoice_vals = super()._prepare_invoice(date_invoice=date_invoice, journal=journal)
        invoice_sub_line = self.invoice_stub_ids.filtered(lambda sub: sub.date == date_invoice)
        invoice_vals['invoice_date'] = invoice_sub_line.date
        invoice_vals['date'] = invoice_sub_line.date

        return invoice_vals


    def _group_by_task(self, invoice_lines):
        new_invoice_lines = []

        for line in invoice_lines:
            if not line[2].get("timesheet_ids"):
                new_invoice_lines.append(line)
                continue

            timesheet_ids = line[2]['timesheet_ids']
            timesheets = self.env['account.analytic.line'].browse(timesheet_ids)
            tasks = timesheets.mapped('task_id')

            for task in tasks:
                # Filter timesheets for this task
                task_timesheets = timesheets.filtered(lambda r: r.task_id.id == task.id)

                new_line = line[2].copy()
                new_line['quantity'] = sum(task_timesheets.mapped('unit_amount'))
                new_line['timesheet_ids'] = task_timesheets.ids
                new_line['name'] = f"{new_line.get('name', '')} - {task.name}"

                new_invoice_lines.append((0, 0, new_line))

                # Add task_stock_info to the invoice line
                task_stock_lines = self._prepare_task_stock(task)
                if task_stock_lines:
                    for stock_line in task_stock_lines:
                        new_invoice_lines.append((0, 0, stock_line))
        return new_invoice_lines


    def _prepare_task_stock(self, task):
        """Prepare stock information for the task"""
        if not task or not hasattr(task, 'move_ids'):
            return
        move_line_vals = []
        for move in task.move_ids: # we can filter this line .filtered(lambda mv: mv.state == 'done')
            logging.warning(f"{move=}")
            invoice_line_vals = {
                'name': f"Stock - {task.name}: {move.name}",
                'product_id': move.product_id.id,
                'quantity': move.product_uom_qty,
                'product_uom_id': move.product_uom.id,
                'analytic_distribution': move.analytic_account_line_ids.ids,
            }
            move_line_vals.append(invoice_line_vals)
        return move_line_vals


    # maybe this parts will be moved
    contract_payment_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')], string="Contract Type", default='percentage')

    down_payment = fields.Float(string="Down Payment (%)")
    final_payment = fields.Float(string="Final Payment (%)")
    total_amount = fields.Float(string="Total Amount")
    fixed_amount = fields.Float(string="Fixed Amount")

    def _get_payment_structure(self):
        """Calculate the payment structure and return payment schedule"""
        if not self.contract_payment_type:
            return None

        start_date = self.date_start
        end_date = self.date_end or (fields.Date.today() + relativedelta(months=+1))
        total_amount = self.total_amount

        if total_amount <= 0:
            return None

        down_payment_amount = (self.down_payment / 100) * total_amount
        final_payment_amount = (self.final_payment / 100) * total_amount

        # Generate ALL possible monthly payment dates
        monthly_range = pd.date_range(start=start_date, end=end_date, freq='MS')

        if len(monthly_range) == 0:
            return None

        # Filter out months that will have special payments
        monthly_dates = []
        for date in monthly_range:
            date_obj = date.date()

            # Skip start month if we have a down payment
            if down_payment_amount > 0 and date_obj.year == start_date.year and date_obj.month == start_date.month:
                continue

            # Skip end month if we have a final payment
            if final_payment_amount > 0 and date_obj.year == end_date.year and date_obj.month == end_date.month:
                continue

            monthly_dates.append(date_obj)

        # Calculate remaining amount to be split across remaining months
        remaining_amount = total_amount - (down_payment_amount + final_payment_amount)
        monthly_payment = remaining_amount / len(monthly_dates) if len(monthly_dates) > 0 else 0

        # Create payment schedule
        payment_schedule = []

        # Add down payment (if exists)
        if down_payment_amount > 0:
            payment_schedule.append({
                'type': 'down_payment',
                'date': start_date,
                'amount': down_payment_amount
            })

        # Add monthly payments (excluding months with special payments)
        for i, payment_date in enumerate(monthly_dates):
            payment_schedule.append({
                'type': 'monthly_payment',
                'installment': i + 1,
                'date': payment_date,
                'amount': monthly_payment
            })

        # Add final payment (if exists)
        if final_payment_amount > 0:
            payment_schedule.append({
                'type': 'final_payment',
                'date': end_date,
                'amount': final_payment_amount
            })

        return payment_schedule

    def _compute_contract_lines(self):
        """Compute contract lines amount based on contract line configuration"""

        # Handle fixed payment type contracts
        if self.contract_payment_type == 'fixed':
            return self.fixed_amount

        # For percentage-based contracts, check payment schedule if we have an active stub date
        if self.contract_payment_type == 'percentage' and not self.date_end:
            raise UserError(_("Kindly set an end date for this contract."))

        if self.contract_payment_type == 'percentage' and self.active_stub_start_date:
            payment_schedule = self._get_payment_structure()
            if payment_schedule:
                # Find the payment for the active stub date or within the same month
                for payment in payment_schedule:
                    # Check if active_stub_start_date is within the same month as payment['date']
                    if self._is_date_in_same_month(self.active_stub_start_date, payment['date']):
                        return payment['amount']

        # Default contract line calculation
        total_price_subtotal = []
        for line in self.contract_line_fixed_ids:
            dates = line._get_period_to_invoice(
                line.last_date_invoiced, line.recurring_next_date
            )
            total_price_subtotal.append(line._get_quantity_to_invoice(*dates) * line.price_unit)

        return sum(total_price_subtotal)

    def _is_date_in_same_month(self, date1, date2):
        """Check if date1 is within the same month and year as date2"""
        if not date1 or not date2:
            return False
        return date1.year == date2.year and date1.month == date2.month

    def _process_stub_for_date(self, invoicing_date):
        """Create or update stub for given date"""
        existing_stub = self.env['contract.invoice.stub'].search([
            ('contract_id', '=', self.id),
            ('date', '=', invoicing_date),
        ])

        # Set the active stub date so _compute_contract_lines can use it
        self.active_stub_start_date = invoicing_date
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
            existing_stub.write({'amount': self._compute_contract_lines()})