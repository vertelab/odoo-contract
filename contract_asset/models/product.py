from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('rent', 'Rent'), ('amortization', 'Amortization')],
                            ondelete={'rent': 'set default', 'amortization': 'set default'})

