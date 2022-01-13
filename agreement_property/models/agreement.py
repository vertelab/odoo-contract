import logging

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class AgreementProperty(models.Model):
    _description = "Agreement Property"
    _inherit = 'agreement'
    _inherits = {
#            'property.property': 'property_id'
            }

#    def _get_default(self, *args, **kwargs):
#        return None


#    @property
#    def employees(self):
#       if not self.property_id:
#            return None
#        return self.property_id.employees

    def _get_employees(self):
        if not self.property_id:
            return None
        return self.property_id.employees


    property_id = fields.Many2one(
            'property.property',
            string="Property",
            required=False,
#            ondelete="cascade",
            default=None,
            )

    employees = fields.Integer(
            string="Employees",
            required=False,
            default=_get_employees,
            )

    @api.onchange("property_id")
    def onchange_property_and_related(self):
        _logger.info("ONCHANGE PROPERTY_ID")
        _logger.info(f"PREVIOUS EMPLOYEES {self.employees}")
        self.employees = self._get_employees()
        _logger.info(f"NEW EMPLOYEES {self.employees}")
     
#    employees = fields.Integer(string="Employees", required=False)

    #TODO: Check if we can use the save & create function (@api.model?) to force updates to sections
    # title when saved?
    # Possibly in this class, possibly in the class AgreementSectionProperty
    # Is it possible to trigger this on update?
    


