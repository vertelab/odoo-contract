import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ContractProject(models.Model):
    _inherit = "contract.contract"
    
    project_id = fields.Many2one('project.project', string='Project')

    def open_timesheet(self):
        self.ensure_one()
        action_window = {
            'type': 'ir.actions.act_window',
            'name': 'Timesheet',
            'res_model': 'account.analytic.line',
            'view_type': 'list',
            'domain': [('project_id', '=', self.project_id.id)],
            'view_mode': 'tree,list',
            'target': 'current',
        }
        return action_window

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        # check if you can reuse existing project or not, otherwise create 
        # _logger.warning(f"outside if statement contract create")
        _logger.warning(f"inside if statement contract create")
        project = self.env['project.project'].create({
            'name': res.name,
            'contract_id': res.id,
            'allow_timesheets': True,
            'label_tasks': 'Jobs'
        })
        return res 

    
