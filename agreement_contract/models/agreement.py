import logging
import datetime

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class AgreementContractWizard(models.TransientModel):
    _name = "agreement.contract.wizard"
    _description = "Agreement Contract Wizard"

    # Strings used in translations
    _rent_title = _("Rent (automatically created)")

    def _get_current_agreement(self):
        return self.env["agreement"].browse(self.env.context.get('active_ids'))

    def _initialize_start_date(self):
        return self._get_current_agreement().start_date

    def _initialize_end_date(self):
        return self._get_current_agreement().end_date


    start_date = fields.Date(
            string="Start date",
            default=_initialize_start_date,
            required=True,
            readonly=True,
            )

    end_date = fields.Date(
            string="End date",
            default=_initialize_end_date,
            required=True,
            readonly=True,
            )

    recurring_interval = fields.Integer(
            string="Recurring interval",
            default=1,
            required=True,
            )

    # Copied from odooext-OCA-contract/contract/models/contract_recurrency_mixin.py
    recurring_rule_type = fields.Selection(
            [
                ("daily", "Day(s)"),
                ("weekly", "Week(s)"),
                ("monthly", "Month(s)"),
                ("monthlylastday", "Month(s) last day"),
                ("quarterly", "Quarter(s)"),
                ("semesterly", "Semester(s)"),
                ("yearly", "Year(s)"),
                ],
            default="monthly",
            string="Recurrence",
            help="Specify Interval for automatic invoice generation.",
            required=True,
            )

    recurring_start_date = fields.Date(
            string="Start of next invoice",
            default=None,
            required=False,
            help="Specify if different to start date",
            )

    cost_per_recurrance = fields.Float(
            string="Cost per recurrance",
            required=True,
            )

    cost_index = fields.Float(
            string="Index increase per year in percent (Triggered at 1/1 every year)",
            required=False,
            )

    def _generate_contract(self, agreement, price_list):
        return self.env["contract.contract"].sudo().create({ #TODO: Verify that this should be sudo
            "name": _("Contract for {}").format(agreement.name),
            "partner_id": agreement.partner_id.id,
            "recurring_interval": self.recurring_interval,
            "recurring_rule_type": self.recurring_rule_type,
            "date_start": self.start_date,
            "date_end": self.end_date,
            "pricelist_id": price_list.id,
            })


    def _generate_price_list_row(self, year, price):
        return {
            "applied_on": "3_global",
            "date_start": datetime.datetime(year, 1, 1),
            "date_end": datetime.datetime(year, 12, 31),
            "compute_price": "fixed",
            "fixed_price": price,
            }

    def _generate_price_list(self, agreement):
        item_ids = []
        for year in range(self.start_date.year, self.end_date.year + 1):
            #TODO: This assumes the formulae COST * (1 + INDEX)  ^ YEAR-DIFF
            quota = (1.0 + self.cost_index / 100) ** (year - self.start_date.year)
            price = self.cost_per_recurrance * quota

            item_ids.append((0,0,self._generate_price_list_row(year, price)))

        return self.env["product.pricelist"].sudo().create({
            "name": _("Price list for {}").format(agreement.name), #TODO: Possibly add some other identification, so that we can find the correct one for a specific year.
            "item_ids": item_ids,
            })

    def _create_rent(self):
        product = self.env["product.product"].search([("name", "=", self._rent_title)])

        if not product:
            _logger.info("Creating product %s", repr(self._rent_title))
            product = self.env["product.product"].sudo().create({
                "name": self._rent_title,
                })
        _logger.warning(product)
        return product

    def _create_contract_line(self, contract_id):
        rent = self._create_rent()

        contract_line_id = self.env["contract.line"].sudo().create({
            "product_id": rent.id,
            "contract_id": contract_id.id,
            "name": self._rent_title,
            "date_start": self.start_date,
            "date_end": self.end_date,
            "recurring_next_date": self.recurring_start_date or self.start_date,
            "automatic_price": True,
#            "state": "in-progress",
            })

    def save_button(self):
        _logger.warning("Save button pressed")
        agreement = self._get_current_agreement()

        price_list = self._generate_price_list(agreement)

        contract_id = self._generate_contract(agreement, price_list)

        agreement.contract_id = contract_id

        contract = self.env["contract.contract"].browse(contract_id)

        contract_line_id = self._create_contract_line(contract_id)


def type_per_year(recurring_rule_type):
    if recurring_rule_type == "daily":
        return 1/365.2425 # TODO: Consider if this year is leap
    elif recurring_rule_type == "weekly":
        return 1/(365.2425/7) # TODO: Consider if this year has 53 weeks
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

    @api.depends("contract_id", "contract_id.contract_line_ids", "contract_id.recurring_rule_type", "contract_id.recurring_interval")
    def _contract_yearly_cost(self):
        #TODO: Consider actual price after every modifier that can be applied to it, such as index-increases.
        #TODO: Consider if the line is 'active' during some type of period, possibly by simulating the year?
        cost_per_year = 0
        try:
            for contract_line in self.contract_id.contract_line_ids:
                line_price = contract_line.price_unit * contract_line.quantity
                period = get_period(self.contract_id, contract_line)
                cost_per_year += line_price / period
        except (TypeError, ZeroDivisionError) as e:
            pass
        self.contract_yearly_cost = cost_per_year

    contract_yearly_cost = fields.Float(
            string="Contracts Yearly cost",
            compute=_contract_yearly_cost,
            )

