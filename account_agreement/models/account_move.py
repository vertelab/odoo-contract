import logging
import datetime

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class AccountMoveAgreement(models.Model):
    _description = "Account Move link to Agreement"
    _inherit = "account.move"

    @api.depends("invoice_line_ids")
    def _calculate_related_agreement(self):
        agreement_id = None

        try:
            for invoice_line_id in self.invoice_line_ids:
                agreement = self.env["agreement"].search([('contract_id', '=', invoice_line_id.contract_line_id.contract_id.id)])
                agreement_id = agreement.id
                break
        except:
            pass

        if agreement_id is None:
            try:
                for invoice_line_id in self.invoice_line_ids:
                    agreement = self.env["agreement"].search([('property_id', '=', invoice_line_id.contract_line_id.contract_id.related_property_id.id)])
                    agreement_id = agreement.id
                    break
            except:
                pass

        self.agreement_agreement_id = agreement_id

    # Would much rather have the name agreement_id
    # The OCA module agreement_account uses this variable in account.move
    # Therefore, the name of this field became agreement_agreement_id
    agreement_agreement_id = fields.Many2one(
            "agreement",
            string="Related agreement",
            compute=_calculate_related_agreement,
            default=None,
            store=True,
            )


