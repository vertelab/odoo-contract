import logging, datetime
from odoo import api, fields, models
from odoo.tools.translate import _
from collections import Iterable
import json
from datetime import date
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ContractContract(models.Model):
    _name = "contract.contract"
    _inherit = [
        'contract.contract',
        'mail.render.mixin'
    ]
    """
    Overrides function in contract.contract, 
    so that we can use jinja when you create an invoice from a contract
    """

    def _prepare_recurring_invoices_values_jinja(self, invoices_values):
        # ~ _logger.info('_prepare_recurring_invoices_values running... date_ref = %s' % date_ref)
        # ~ invoices_values = super()._prepare_recurring_invoices_values(date_ref)
        for inv in invoices_values:
            inv['narration'] = self.note
            inv['narration'] = self._render_template_jinja(

                inv['narration'],
                "contract.contract",
                [self.id]
            )
            tp = str(inv['narration']).split("'", 1)
            tp = tp[1][:-2]
            tp = tp.replace('\\n', '\n')
            inv['narration'] = tp

            n = 0
            for line in inv['invoice_line_ids']:
                line[2]['name'] = self._render_template_jinja(

                    line[2]['name'],
                    "contract.line",
                    [self.contract_line_ids[n].id]
                )
                tp = str(line[2]['name']).split("'", 1)
                tp = tp[1][:-2]
                tp = tp.replace('\\n', '\n')
                line[2]['name'] = tp
                n = n + 1

        # ~ _logger.warning(f"{invoices_values=}")
        return invoices_values

    def _prepare_recurring_invoices_values(self, date_ref=False):
        """
        This method builds the list of invoices values to create, based on
        the lines to invoice of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        invoices_values = []
        for contract in self:
            if not date_ref:
                date_ref = contract.recurring_next_date
            if not date_ref:
                # this use case is possible when recurring_create_invoice is
                # called for a finished contract
                continue
            contract_lines = contract._get_lines_to_invoice(date_ref)
            if not contract_lines:
                continue
            invoice_vals, move_form = contract._prepare_invoice(date_ref)
            invoice_vals["invoice_line_ids"] = []
            for line in contract_lines:
                invoice_line_vals = line._prepare_invoice_line(move_form=move_form)
                if invoice_line_vals:
                    # Allow extension modules to return an empty dictionary for
                    # nullifying line. We should then cleanup certain values.
                    del invoice_line_vals["company_id"]
                    del invoice_line_vals["company_currency_id"]
                    invoice_vals["invoice_line_ids"].append((0, 0, invoice_line_vals))
            invoices_values.append(invoice_vals)
            # Force the recomputation of journal items
            del invoice_vals["line_ids"]

            invoices_values = self._prepare_recurring_invoices_values_jinja(invoices_values)
            contract_lines._update_recurring_next_date()
        return invoices_values

    def get_strftime_month(self, format_list):
        if self.next_period_date_start.strftime("%m") != self.next_period_date_end.strftime("%m"):
            return self.get_strftime_start(format_list) + " - " + self.get_strftime_end(format_list)
        else:
            return self.get_strftime_start(format_list)

    def get_strftime_start(self, format_list):
        return " ".join([self.recurring_next_date.strftime(f) for f in format_list])

    def get_strftime_end(self, format_list):
        return " ".join([self.next_period_date_end.strftime(f) for f in format_list])


class ContractLine(models.Model):
    _inherit = 'contract.line'

    def get_strftime_month(self, format_list):
        if self.next_period_date_start.strftime("%m") != self.next_period_date_end.strftime("%m"):
            return self.get_strftime_start(format_list) + " - " + self.get_strftime_end(format_list)
        else:
            return self.get_strftime_start(format_list)

    def get_strftime_start(self, format_list):
        return " ".join([self.next_period_date_start.strftime(f) for f in format_list])

    def get_strftime_end(self, format_list):
        return " ".join([self.next_period_date_end.strftime(f) for f in format_list])


class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

    @staticmethod
    def date_decoder(dct):
        for key, value in dct.items():
            if isinstance(value, str) and value.startswith("DATE:"):
                date_string = value.split("DATE:")[1]
                dct[key] = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

        return dct


"""
JSON stringify does not work on the original date format, 
so we convert it to a date format that works for json stringify, 
and then convers it back
"""
