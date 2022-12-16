import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ProjectContract(models.Model):
    _inherit = "project.project"
    
    contract_id = field_name_id = fields.Many2one('contract.contract', string='Contract')