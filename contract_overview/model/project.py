from odoo import models, fields, api


class Project(models.Model):
    _inherit = "project.project"

    def action_view_contract_overview(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "contract_overview.contract_overview_action_client")
        action['params'] = {
            'project_ids': self.ids,
        }
        action['context'] = {
            'active_id': self.id,
            'active_ids': self.ids,
            'search_default_name': self.name,
        }
        return action