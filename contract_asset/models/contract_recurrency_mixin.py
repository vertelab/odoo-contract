from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class OverrideContractRecurrencyMixin(models.AbstractModel):
    _inherit = "contract.recurrency.mixin"

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        """Return a relativedelta for one period.

        When added to the first day of the period,
        it gives the first day of the next period.
        """
        if recurring_rule_type == "daily":
            return relativedelta(days=interval)
        elif recurring_rule_type == "weekly":
            return relativedelta(weeks=interval)
        elif recurring_rule_type == "monthly":
            return relativedelta(months=interval)
        elif recurring_rule_type == "monthlylastday":
            return relativedelta(months=interval, day=31)
        elif recurring_rule_type == "quarterly":
            return relativedelta(months=3 * interval)
        elif recurring_rule_type == "semesterly":
            return relativedelta(months=6 * interval)
        else:
            return relativedelta(years=interval)