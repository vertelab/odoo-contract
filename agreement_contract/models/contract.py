import logging
import datetime

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class ContractAbstractContractLine(models.AbstractModel):
    _inherit = "contract.recurrency.basic.mixin"
    _description = "Extend functionallity for date-specific pricelists"

    def _compute_date(self, line):
        return line.contract_id.recurring_next_date or fields.Date.context_today(line)

    @api.depends(
        "automatic_price",
        "specific_price",
        "product_id",
        "quantity",
        "contract_id.pricelist_id",
        "contract_id.partner_id",
    )
    def _compute_price_unit(self):
        """Get the specific price if no auto-price, and the price obtained
        from the pricelist otherwise.
        """
        super(ContractAbstractContractLine, self)._compute_price_unit()

        for line in self:
            if line.automatic_price:
                pricelist = (
                    line.contract_id.pricelist_id
                    or line.contract_id.partner_id.with_company(
                        line.contract_id.company_id
                    ).property_product_pricelist
                )
                product = line.product_id.with_context(
                    quantity=line.env.context.get(
                        "contract_line_qty",
                        line.quantity,
                    ),
                    pricelist=pricelist.id,
                    partner=line.contract_id.partner_id.id,
                    date=line.env.context.get(
                        "old_date", self._compute_date(line)
                    ),
                )
                if line.price_unit != product.price:
                    line.price_unit = product.price


class ContractRecurrencyMixin(models.AbstractModel):
    _inherit = "contract.recurrency.basic.mixin"
    _description = "Bugfix for recurrency mixin"

    # Overrides base function in contract.contract
    @api.model
    def get_next_period_date_end(
        self,
        next_period_date_start,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
        next_invoice_date=False,
        recurring_invoicing_type=False,
        recurring_invoicing_offset=False,
    ):
        next_period_date_end = super(AgreementContract, self).get_next_period_date_end(
                next_period_date_start,
                recurring_rule_type,
                recurring_interval,
                max_date_end,
                next_invoice_date,
                recurring_invoicing_type,
                recurring_invoicing_offset,
                )
        if recurring_rule_type == "monthlylastday":
            if not next_invoice_date or recurring_invoicing_type == "pre-paid":
                next_period_date_end += timedelta(days=35)
                next_period_date_end -= timedelta(days=next_period_date_end.day + 1)
            if max_date_end and next_period_date_end > max_date_end:
                next_period_date_end = max_date_end
        return next_period_date_end


