import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _

class SaleOrderModify(models.Model):
    _inherit = "sale.order"

    # def create_contracts(self, order):
    #     result = super(SaleOrderModify,self).create_contracts(order)
    #     _logger.warning("create_contracts SaleOrderModify"*100)
    #     _logger.warning(f"{order=}")
    #     _logger.warning(f"{result=}")
    #     for contract in result:
    #         contract.sale_id.order_line
            
    #         projects = order.order_line.mapped('product_id.project_id')
    #         projects |= order.order_line.mapped('project_id')
    #         projects |= order.project_id
    #         order.project_ids = projects

    #     return result

    # @api.depends('order_line.product_id', 'order_line.project_id')
    # def _compute_project_ids(self):
    #     for order in self:
    #         _logger.warning(f"inside compute_project_ids loop HELLO")
    #         projects = order.order_line.mapped('product_id.project_id')
    #         projects |= order.order_line.mapped('project_id')
    #         projects |= order.project_id
    #         order.project_ids = projects

    # def hello(self):
    #     self._compute_project_ids()