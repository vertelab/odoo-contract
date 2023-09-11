from odoo import models, fields, api


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _insert_markers(self, first_date_invoiced, last_date_invoiced):
        self.ensure_one()
        lang_obj = self.env["res.lang"]
        lang = lang_obj.search([("code", "=", self.contract_id.partner_id.lang)])
        date_format = lang.date_format or "%m/%d/%Y"
        name = self.name
        name = name.replace("#START#", first_date_invoiced.strftime(date_format))
        name = name.replace("#END#", last_date_invoiced.strftime(date_format))
        # ~ https://www.tutorialspoint.com/How-to-get-formatted-date-and-time-in-Python
        # ~ name = name.replace("#YEAR#", last_date_invoiced.strftime(date_format))
        name = name.replace("#YEAR#", last_date_invoiced.strftime("%Y"))
        name = name.replace("#MONTH#", last_date_invoiced.strftime("%M"))
        return name
