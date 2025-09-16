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

    @api.depends("property_id", "property_id.municipality_id")
    def _municipality(self):
        for record in self:
            if not record.property_id:
                continue
            _logger.warning(record.property_id.municipality_id)
            _logger.warning(record.property_id.municipality_id.id)
            record.municipality_id = record.property_id.municipality_id.id

    municipality_id = fields.Many2one(
        comodel_name='res.country.municipality',
        string='Municipality',
        compute=_municipality,
        store=True,
    )



    @api.depends("property_id", "property_id.employees")
    def _employees(self):
        if not self.property_id:
            return
        self.employees = self.property_id.employees

    employees = fields.Integer(
            string="Employees",
            required=False,
            compute=_employees,
            store=True,
            )

    #TODO: Check if we can use the save & create function (@api.model?) to force updates to sections
    # title when saved?
    # Possibly in this class, possibly in the class AgreementSectionProperty
    # Is it possible to trigger this on update?



