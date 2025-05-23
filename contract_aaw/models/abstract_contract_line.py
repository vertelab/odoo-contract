# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractAbstractContractLine(models.AbstractModel):
    _inherit = "contract.abstract.contract.line"

    qty_type = fields.Selection(selection_add=[('aaw', 'AAW'),], ondelete={'aaw': 'cascade'})

## if odoo version >= 18 then... 
#class ContractAbstractContractLine(models.AbstractModel):
#    _inherit = "contract.abstract.contract.line"

    #qty_type = fields.Selection([
    #    ('foo', 'Foo'),
    #    ('bar', 'Bar'),
    #    ('aaw', 'AAW'),
    #], string="Quantity Type", ondelete={'aaw': 'cascade'})
