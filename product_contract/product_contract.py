from openerp import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

class product_contract_wizard(models.TransientModel):
    _name = 'product.contract.wizard'

    #template_id = fields.Many2one(comodel_name='account.analytic.account', string='Template of Contract', domain=(['type', '=', 'template']))

    @api.one
    def create_contract(self):
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
                line.contract_id = contract.copy({
                    'type': 'contract',
                    'template_id': contract.id,
                    'partner_id': self.partner_id.id,
                    'date_start': contract.get_contract_start(),
                })
                # kopiera fakturaraden från mallen, multiplicera antalet på alla fakturarader med antalet prenumerationer
                #recurring_next_date = timedelta recurring_interval + 1 recurring_rule_type från inital recurring_next_date tills vi passerat dagens datum (om recurring_invoce True)
                line.contract_id.name = self.name
                self.project_id = line.contract_id
        
        
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
            
