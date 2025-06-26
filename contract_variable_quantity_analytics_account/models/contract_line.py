from odoo import api, fields, models, _
from odoo.exceptions import UserError

import datetime
from datetime import date, datetime

import logging

_logger = logging.getLogger(__name__)

class ContractLine(models.Model):
    _inherit = "contract.line"
    
    def _contract_variable_quantity_analytics_account_method(self):
        product_quantity = 0
        if self.id:
            amls = self.env['account.move.line'].search([
                 ('move_id.move_type', '=', 'in_invoice'),
                 ('move_id.state','=','posted'),
                 ('product_id.id','=',self.product_id.id),
                 ('analytic_account_id.id','=',self.analytic_account_id.id),
                 ('contract_line_id','=', None)])
            for aml in amls:
                if aml.move_id.invoice_date <= self.next_period_date_end:
                    product_quantity += aml.quantity
                    aml.contract_line_id = self.id
        return (product_quantity)
