import logging
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

def type_per_year(recurring_rule_type):
    if recurring_rule_type == "daily":
        return 1/365.2425 # TODO: Consider if this year is leap
    elif recurring_rule_type == "weekly":
        return 7 * type_per_year("daily")
    elif recurring_rule_type in ("monthly", "monthlylastday"):
        return 1/12
    elif recurring_rule_type == "quarterly":
        return 1/4
    elif recurring_rule_type == "semesterly":
        return 1/2

    else:
        return 1

def get_period(contract, contract_line):
    interesting = contract if contract.line_recurrence is False else contract_line

    period = interesting.recurring_rule_type
    interval = interesting.recurring_interval

    return type_per_year(period) * interval

class AgreementContract(models.Model):
    _description = "Agreement Contract"
    _inherit = "agreement"

    contract_id = fields.Many2one(
            "contract.contract",
            string="Contract",
            required=False,
            default=None,
            )

    contract_yearly_cost = fields.Float(
            string="Contracts Yearly cost",
            compute="_contract_yearly_cost",
            )

    @api.model
    def update_cron_job(self):
        cron_job = self.env.ref("contract.contract_cron_for_invoice")
        cron_job.interval_number = 1
        cron_job.interval_type = "hours"

    @api.depends("contract_id", "contract_id.contract_line_ids", "contract_id.recurring_rule_type", "contract_id.recurring_interval")
    def _contract_yearly_cost(self):
        _logger.warning(f"Recalculating contract yerly cost! {len(self)}")
        for record in self:
            cost_per_year = 0
            try:
                for contract_line in record.contract_id.contract_line_ids:
                    line_price = contract_line.price_unit * contract_line.quantity
                    period = get_period(record.contract_id, contract_line)
                    cost_per_year += line_price / period
            except (TypeError, ZeroDivisionError) as e:
                _logger.error(e)
            record.contract_yearly_cost = cost_per_year
            # Does not seem to trigger on update by itself, force it.
            try:
                record._yearly_cost()
            except AttributeError:
                _logger.warning("Missing module defining function _yearly_cost()")


# TODO: Move to new module?
class AgreementExtension(models.Model):
    _description = "Agreement Extension"
    _inherit = "agreement"

    agreement_number = fields.Char(
            string="Agreement number ESV (Ekonomistyrningsverket)",
            )

