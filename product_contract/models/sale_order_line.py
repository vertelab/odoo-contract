import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ContractAbstractSaleOrderAdd(models.AbstractModel):
    _inherit = "contract.abstract.contract.line"

    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line')
    @api.depends("sale_order_line_id", "sale_order_line_id.task_id", "sale_order_line_id.project_id")
    def compute_project_id(self):
        _logger.warning("compute_project_id" * 100)
        for rec in self:
            _logger.warning(f"{rec=} {rec.sale_order_line_id.task_id=} {rec.sale_order_line_id.project_id=}")
            if rec.sale_order_line_id.task_id:
                rec.project_id = rec.sale_order_line_id.task_id.project_id
            else:
                rec.project_id = rec.sale_order_line_id.project_id

    project_id = fields.Many2one(comodel_name="project.project", compute="compute_project_id", readonly=False, store=True)