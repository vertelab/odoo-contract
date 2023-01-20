import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class SaleOrderModify(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project(self):
        res = super()._timesheet_create_project()
        for contract in res.sale_order_id.contract_ids:
            contract.project_id.sale_order_id = res.sale_order_id
            contract.project_id.allow_billable = res.allow_billable
            contract.project_id.bill_type = res.bill_type

        return res