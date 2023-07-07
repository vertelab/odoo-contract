from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

class ContractContract(models.Model):
    _inherit = "contract.contract"

    # @api.model_create_multi
    # def create(self, vals_list):
    #     _logger.error(f"{vals_list=}")
    #     records = super().create(vals_list)
    #     records._set_start_contract_modification()
    #     return records

    def _recurring_create_invoice(self, date_ref=False):
        invoices_values = self._prepare_recurring_invoices_values(date_ref)
        moves = self.env["account.move"].create(invoices_values)
        self._add_contract_origin(moves)
        self._invoice_followers(moves)
        self._compute_recurring_next_date()
        _logger.error(f"{moves=}")
        return moves
    
    def _prepare_recurring_invoices_values(self, date_ref=False):
        invoices_values = super()._prepare_recurring_invoices_values(date_ref)
        _logger.error(f"{invoices_values=}")
        return invoices_values