import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ProjectContract(models.Model):
    _inherit = "project.project"
    
    contract_id = fields.Many2one('contract.contract', string='Contract')

    @api.model_create_multi
    def create(self, vals_list):
        projects = self.env["project.project"]
        for vals in vals_list:
            res = super().create(vals)
            if vals.get('contract_id', False) != False:
                res.contract_id.project_id = res.id

            if res.sale_order_id:
                res.sale_order_id.contract_ids += res.sale_order_id.project_ids.sale_order_id.contract_ids

            projects += res
        return projects

    def open_contract(self):
        if self.contract_id.id != False:
            action_window = {
                'type': 'ir.actions.act_window',
                'name': 'Contract',
                'res_model': 'contract.contract',
                'view_type': 'form',
                'res_id': self.contract_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            action_window = {
                'type': 'ir.actions.act_window',
                'name': 'Contract',
                'res_model': 'contract.contract',
                'view_type': 'form',
                'domain': [('id', 'in', self.sale_order_id.contract_ids.ids)],
                'view_mode': 'tree,form',
                'target': 'current',
            }    
        
        return action_window

    # def action_view_so(self):
    #     if self.sale_order_id == False:
    #         self.sale_order_id = self.contract_id[0].sale_id.id

    #     super().action_view_so()
            
        

