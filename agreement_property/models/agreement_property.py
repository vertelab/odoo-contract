import logging

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class AgreementProperty(models.Model):
    _description = "Agreement Property"
    _inherit = 'agreement'
    _inherits = {
            'property.property': 'property_id'
            }


    property_id = fields.Many2one(
            'property.property',
            string="Property",
            required=False,
            ondelete="cascade"
            )

    employees = fields.Integer(string="Employees", required=False, ondelete="cascasde", tracking=True)



class AgreementSectionProperty(models.Model):
    #_description = "Agreement Sections Property"
    _inherit = "agreement.section"
#    _order = "sequence"
    _inherits = {
            'property.property': 'property_id'
            }


    property_id = fields.Many2one(
            'property.property',
            string="Property",
            required=False,
            ondelete="cascade"
            )

    employees = fields.Integer(
            related='property_id.employees',
            )
#            string="Employees",
#            required=False,
#            ondelete="cascasde",
#            tracking=True,
#            )
#    _logger.critical(dir(property_id))

