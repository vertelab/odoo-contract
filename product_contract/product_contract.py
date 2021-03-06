# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015- Vertel AB (<http://www.vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import api, models, fields, _
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class product_contract_wizard(models.TransientModel):
    _name = 'product.contract.wizard'

    #template_id = fields.Many2one(comodel_name='account.analytic.account', string='Template of Contract', domain=(['type', '=', 'template']))

    @api.one
    def create_invoice(self):
        for contract in self.env['account.analytic.account'].browse(self._context.get('active_ids')):
            contract.recurring_create_invoice()
     


class product_template(models.Model):
    _inherit = 'product.template'
    
    contract_id = fields.Many2one(comodel_name='account.analytic.account',
        string='Contract', domain=[('type', '=', 'template')])
    

class order_line(models.Model):
    _inherit = 'sale.order.line'
    
    contract_id = fields.Many2one(comodel_name='account.analytic.account',
        string='Contract', domain=[('type', '=', 'contract')])
        
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    @api.one
    def generate_contract(self):
        """Check order lines for products with contracts, and generate new contracts from them."""
        _logger.warn("generating contract")
        for line in self.order_line:
            if line.product_id and line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.contract_id:
                contract = line.product_id.product_tmpl_id.contract_id
                values = {
                    'type': 'contract',
                    'template_id': contract.id,
                    'partner_id': self.partner_id.id,
                    'date_start': fields.Date.today(),
                    }
                if contract.recurring_invoices:
                    values['recurring_next_date'] = contract.get_first_invoice_date()
                line.contract_id = contract.copy(values)
                for c_line in line.contract_id.recurring_invoice_line_ids:
                    c_line.quantity *= line.product_uom_qty
                
                line.contract_id.name = self.name
                self.project_id = line.contract_id
        
        
class contract(models.Model):
    _inherit = 'account.analytic.account'
    
    @api.multi
    def get_first_invoice_date(self):
        """Return the date of the first invoice"""
        today = fields.Date.from_string(fields.Date.today())
        time = fields.Date.from_string(self.recurring_next_date)
        if self.recurring_rule_type == 'daily':
            deltaT = relativedelta(days = self.recurring_interval)
        elif self.recurring_rule_type == 'weekly':
            deltaT = relativedelta(weeks = self.recurring_interval)
        elif self.recurring_rule_type == 'monthly':
            deltaT = relativedelta(months = self.recurring_interval)
        elif self.recurring_rule_type == 'yearly':
            deltaT = relativedelta(years = self.recurring_interval)
        while time < today:
            time += deltaT
        
        #First invoice is generated by the product, so skip to the second invoice here
        time += deltaT
        
        return fields.Date.to_string(time)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
