from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError, UserError
import logging

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



