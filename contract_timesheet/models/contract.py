import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ContractProject(models.Model):
    _inherit = "contract.contract"
    
    project_id = field_name_id = fields.Many2one('project.project', string='Project')