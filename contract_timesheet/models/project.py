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
            projects += res
        return projects

