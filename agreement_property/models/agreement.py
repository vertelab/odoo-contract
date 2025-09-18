import logging

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class Property(models.Model):
    _description = "Agreement Property"
    _inherit = 'property.property'
    
    #agreement_ids = fields.One2many('agreement', inverse='property_id')
    
    def action_agreement(self):
        type_id = self.env.ref('agreement_legal.agreement_type_contract').id
        return {
            'name': _("Agreements"),
            'type': 'ir.actions.act_window',
            'res_model':'agreement',
            'view_mode': 'kanban,list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {
                'default_property_id': self.id,
                'default_name':self.name,
                'default_agreement_type_id':type_id,
            }
        }


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



