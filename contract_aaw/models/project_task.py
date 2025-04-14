from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = "project.task"

    is_aaw = fields.Boolean(string="Is AAW")