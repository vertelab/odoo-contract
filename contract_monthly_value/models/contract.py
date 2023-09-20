from odoo import models, fields, api


class ContractContract(models.Model):
    _inherit = "contract.contract"
    
    @api.depends('contract_line_ids','contract_line_ids.price_subtotal','recurring_rule_type','recurring_interval' )
    def _monthly_value(self):
        for contract in self:
            monthlySum=sum(contract.contract_line_ids.mapped('price_subtotal'))
            
            if contract.recurring_rule_type=='daily':
                contract.monthly_value = monthlySum/contract.recurring_interval*30
            elif contract.recurring_rule_type=='weekly':
                contract.monthly_value = monthlySum/contract.recurring_interval*4
            elif contract.recurring_rule_type=='monthly' or contract.recurring_rule_type=='monthlylastday':
                contract.monthly_value = monthlySum/contract.recurring_interval
            elif contract.recurring_rule_type=='quarterly':
                contract.monthly_value = monthlySum/3*contract.recurring_interval
            elif contract.recurring_rule_type=='semesterly':
                contract.monthly_value = monthlySum/6*contract.recurring_interval
            elif contract.recurring_rule_type=='yearly':
                contract.monthly_value = monthlySum/12*contract.recurring_interval
            else:
                contract.monthly_value = 0.0
    
    monthly_value=fields.Float(string='Mothly Value', compute='_monthly_value',stored=True)
