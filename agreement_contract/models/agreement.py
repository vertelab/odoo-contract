import logging

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)

def type_per_year(self, recurring_rule_type):
    if recurring_rule_type == "daily":
        return 1/365.2425 # TODO: Consider if this year is leap
    elif recurring_rule_type == "weekly":
        return 1/52 # TODO: Consider if this year has 53 weeks
    elif recurring_rule_type in ("monthly", "monthlylastday"):
        return 1/12
    elif recurring_rule_type == "quarterly":
        return 1/4
    elif recurring_rule_type == "semesterly":
        return 1/2
    else:
        return 1


class AgreementContract(models.Model):
    _description = "Agreement Contract"
    _inherit = 'agreement'
    _inherits = {
            }

    contract_id = fields.Many2one(
            'contract.contract',
            string="Contract",
            required=False,
            default=None,
            )

    @api.depends("contract_id", "contract_id.contract_line_ids", "contract_id.recurring_rule_type", "contract_id.recurring_interval")
    def _yearly_cost(self):
        # TODO: Consider 'self.contract_id.line_reccurance'
        cost_per_year = 0
        try:
            unit_sum = 0

            for contract_line in self.contract_id.contract_line_ids:
                line_price = contract_line.price_unit * contract_line.quantity


                unit_sum += line_price


            period = type_per_year(self.contract_id.recurring_rule_type)
            cost_per_year = unit_sum / (self.contract_id.recurring_interval * period)
        except (TypeError, ZeroDivisionError) as e:
            _logger.warning(e)
        self.yearly_cost = cost_per_year

    yearly_cost = fields.Float(
            string="Yearly cost",
            compute=_yearly_cost,
            )
