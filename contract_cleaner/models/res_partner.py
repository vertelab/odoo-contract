from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

class product_template(models.Model):
    _inherit = "res.partner"

    skill_ids = fields.Many2many('res.skill', string='Skills')