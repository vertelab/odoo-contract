from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

class ResPartnerAllergy(models.Model):
    _inherit = "res.partner"

    allergy_ids = fields.Many2many('res.allergy', string='Allergies')