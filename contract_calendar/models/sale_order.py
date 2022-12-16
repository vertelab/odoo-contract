from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrderModifyContract(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        for contract in self.contract_ids:
            contract.unlink()
        
        res = super(SaleOrderModifyContract,self).action_cancel()
        return res