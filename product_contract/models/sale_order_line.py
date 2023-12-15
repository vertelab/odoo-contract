import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ContractAbstractSaleOrderAdd(models.AbstractModel):
    _inherit = "contract.abstract.contract.line"

    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line')
