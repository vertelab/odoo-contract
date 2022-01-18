import logging
import datetime

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class ContractAgreement(models.Model):
    _description = "Contract Agreement"
    _inherit = "contract.contract"

    has_unpaid_invoice = fields.Boolean(
            string="Has unpaid invoice",
            default=False,
            compute="_has_unpaid_invoice",
            stored=True,
            )

    @api.depends("recurring_next_date")
    def _has_unpaid_invoice(self):
        for record in self:
            invoices = record._get_related_invoices()
            for invoice in invoices:
                _logger.warning(invoice.payment_state)
                if invoice.payment_state == 'not_paid':
                    record.has_unpaid_invoice = True
                    break
            else:
                record.has_unpaid_invoice = False

            _logger.warning(invoices)





