from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError, UserError


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _insert_markers(self, first_date_invoiced, last_date_invoiced):
        self.ensure_one()
        lang_obj = self.env["res.lang"]
        lang = lang_obj.search([("code", "=", self.contract_id.partner_id.lang)])
        date_format = lang.date_format or "%m/%d/%Y"
        name = self.name
        name = name.replace("#START#", first_date_invoiced.strftime(date_format))
        if last_date_invoiced:
            name = name.replace("#END#", last_date_invoiced.strftime(date_format))
        name = name.replace(
            "#INVOICEMONTHNAME#",
            self.with_context(lang=lang.code)._translate_marker_month_name(
                first_date_invoiced.strftime("%m")
            ),
        )
        return name


    def _prepare_invoice_line(self):
        res = super()._prepare_invoice_line()

        if self.qty_type == "aaw":
            if self.contract_id.recurring_rule_type != "monthly":
                raise UserError(_("AAW module can't handle other types of intervals yet."))

            if self.analytic_distribution:
                invoice_from_date = self.contract_id.active_stub_start_date - relativedelta(
                    months=self.contract_id.recurring_interval)
                invoice_to_date = self.contract_id.active_stub_end_date - relativedelta(
                    months=self.contract_id.recurring_interval)
                domain = self._analytic_domain(invoice_from_date=invoice_from_date, invoice_to_date=invoice_to_date)

                analytic_line_id = self.env['account.analytic.line'].search(domain)
                if analytic_line_id:
                    res["quantity"] = sum(analytic_line_id.mapped('unit_amount'))
                    res['timesheet_ids'] = analytic_line_id.ids

        if self.qty_type == "aaw" and self.analytic_distribution and not res.get('timesheet_ids', False):
            return None
        return res

    def _analytic_domain(self, invoice_from_date, invoice_to_date):
        account_domain = []

        # domain for multiple analytic accounts
        for key in self.analytic_distribution:
            account_id = int(key)
            if account_domain:
                account_domain = ['|'] + [('account_id', '=', account_id)] + account_domain
            else:
                account_domain = [('account_id', '=', account_id)]

        # Get the hour UOM ID
        time_uom_id = self.env.ref('uom.product_uom_hour').id

        domain = account_domain + [
            ('product_uom_id', '=', time_uom_id),
            ('date', '>=', invoice_from_date),
            ('date', '<=', invoice_to_date),
            ('task_id', '!=', False),
            ('task_id.is_aaw', '=', True),
            ('timesheet_invoice_id', '=', False),
        ]
        return domain



