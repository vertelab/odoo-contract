from openerp import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

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
                line.contract_id = contract.copy({
                    'type': 'contract',
                    'template_id': contract.id,
                    'partner_id': self.partner_id.id,
                    'date_start': contract.get_contract_start(),
                })
                
class contract(models.Model):
    _inherit = 'account.analytic.account'
    
    contract_start_delay = fields.Selection([('today', 'Today'), ('week', 'Next week'), ('month', 'Next month')], string="Start delay after purchase", default='today')
    
    @api.multi
    def get_contract_start(self):
        """Return the startdate of the contract"""
        if self.contract_start_delay == 'today':
            return fields.Date.today()
        elif self.contract_start_delay == 'week':
            pass
        elif self.contract_start_delay == 'week':
            pass
            
