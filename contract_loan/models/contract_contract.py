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
           new_invoice_vals = []
           for line in invoice_vals['invoice_line_ids']:
               if isinstance(line[2], list):
                   for invoice_line in line[2]:
                       new_invoice_vals.append((0, 0, invoice_line))
               else:
                   new_invoice_vals.append(line)
           invoice_vals['invoice_line_ids'] = new_invoice_vals

        return invoices_values
