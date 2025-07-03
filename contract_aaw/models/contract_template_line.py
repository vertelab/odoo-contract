# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ContractTemplateLine(models.Model):
    _inherit = "contract.template.line"

    qty_type = fields.Selection(selection_add=[
        ('aaw', 'AAW'), ('fixed/percentage', 'Fixed/Percentage')
    ], ondelete={'aaw': 'cascade', 'fixed/percentage': 'cascade'}, fixed='percentage')

