from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

class ResAllergy(models.Model):
    _name = "res.allergy"
    _description = "A model for tags added to res.partner"

    name = fields.Char('Name', required=True)
    color = fields.Integer(string='Color')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]