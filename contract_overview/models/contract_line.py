from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

class ContractLine(models.Model):
    _inherit = "contract.line"

    contract_overview = fields.Boolean()
    invoice_ids = fields.Many2one('account.move.line')

class ContractTemplateLine(models.Model):
    _inherit = "contract.template.line"

    contract_overview = fields.Boolean()

class ContractAbstractContractLine(models.AbstractModel):
    _inherit = "contract.abstract.contract.line"

    contract_overview = fields.Boolean()
