import logging

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class AgreementProperty(models.Model):
    _description = "Agreement Property"
    _inherit = 'agreement'

    def _get_employees(self):
        if not self.property_id:
            return None


    property_id = fields.Many2one(
            'property.property',
            string="Property",
            required=False,
            default=None,
            )

    @api.depends("property_id", "property_id.employees")
    def onchange_property_and_related(self):
        if not self.property_id:
            return
        self.employees = self.property_id.employees

    employees = fields.Integer(
            string="Employees",
            required=False,
            compute=onchange_property_and_related,
            store=True,
            )

    #TODO: Check if we can use the save & create function (@api.model?) to force updates to sections
    # title when saved?
    # Possibly in this class, possibly in the class AgreementSectionProperty
    # Is it possible to trigger this on update?



