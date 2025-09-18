import logging
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AgreementContractWizard(models.TransientModel):
    _name = "agreement.contract.wizard"
    _description = "Agreement Contract Wizard"

    default_product_title = "Rent (automatically created)"

    def _get_product_title(self):
        return self.default_product_title

    def _initialize_start_date(self):
        try:
            return self.agreement_id.start_date
        except AttributeError:
            return None

    def _initialize_end_date(self):
        try:
            return self.agreement_id.end_date
        except AttributeError:
            return None

    def _get_contract_name(self, name):
        return _("Contract for {}").format(name)

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
    cost_per_recurrence = fields.Float(
            string="Cost per recurrence",
            required=True,
            )
    type_of_cost_increase = fields.Selection([
        ("index", "Index increase"),
        ("percent", "Percent increase"),
    ], string="Type of cost increase", required=True,
    )
    cost_index = fields.Float(
            string="Cost increase per year in percent (Triggered at 1/1 every year)",
            required=False,
            )
    consumer_index_base_year = fields.Many2one(
            "consumer.price.index",
            string="Cost is evaluated based on this years CPI",
            required=False,
            )
    contract_template_id = fields.Many2one(comodel_name="contract.template")

    agreement_id = fields.Many2one('agreement', string="Agreement")

    contract_yearly_cost = fields.Float(
        string="Contracts Yearly cost",
        related='agreement_id.contract_yearly_cost',
        readonly=False
    )

    def _generate_contract(self, agreement, price_list):

        if not agreement.partner_id:
            raise UserError("In order to create a contract a partner needs to be specified on the agreement.")

        contract_id = self.env["contract.contract"].sudo().create({
            "name": self._get_contract_name(agreement.name),
            "partner_id": agreement.partner_id.id,
            "recurring_interval": self.recurring_interval,
            "recurring_rule_type": self.recurring_rule_type,
            "date_start": self.start_date,
            "date_end": self.end_date,
            "pricelist_id": price_list.id,
            "contract_template_id": self.contract_template_id.id,
            "consumer_index_base_year_id": self.consumer_index_base_year.id
        })

        contract_id._onchange_contract_template_id()
        return contract_id

    # def _generate_price_list_row(self, year, price, indexed=False):
    #     data = {
    #         "applied_on": "3_global",
    #         "date_start": datetime.datetime(year, 1, 1),
    #         "date_end": datetime.datetime(year, 12, 31),
    #         "fixed_price": price,
    #         }

    #     if indexed is False:
    #         data["compute_price"] = "fixed"
    #     else:
    #         data["compute_price"] = "by_index"
    #         if self.env["consumer.price.index"].search([('year', '=', year)]).id is False:
    #             # TODO: Somehow inform user that this has been setup and remind that it has to be filled.
    #             cpi_row = self.env["consumer.price.index"].sudo().create(
    #                     {
    #                         'year': year,
    #                         'index': -1,
    #                         }).id
    #         data["year"] = year

    #     return data

    # def _calculate_price_list_row(self, year):
        # if self.type_of_cost_increase == 'index':
        #     base_price = self.cost_per_recurrance / self.consumer_index_base_year.index
        #     # TODO: Error if year has negative index
        #     return self._generate_price_list_row(year, base_price, indexed=True)
        # elif self.type_of_cost_increase == 'percent':
        #     #TODO: This assumes the formulae COST * (1 + INDEX)  ^ YEAR-DIFF
        #     quota = (1.0 + self.cost_index / 100) ** (year - self.start_date.year)
        #     price = self.cost_per_recurrance * quota
        #     return self._generate_price_list_row(year, price)
        # elif self.type_of_cost_increase == 'none':
        #     return self._generate_price_list_row(year, self.cost_per_recurrance)
        # else:
        #     raise NotImplementedError

    # def _generate_price_list(self, agreement):
    #     return self.env["product.pricelist"].sudo().create({
    #         "name": _("Price list for {}").format(agreement.name), #TODO: Possibly add some other identification, so that we can find the correct one for a specific agreement.
    #         "item_ids": [(0, 0, self._calculate_price_list_row(year))
    #                      for year in range(self.start_date.year, self.end_date.year + 1)],
    #         })

    def _create_price_list(self,agreement):
        start_year = self.recurring_start_date.year
        return self.env["product.pricelist"].sudo().create({
            "name": _(f"Price list for {agreement.name}"),
            "item_ids": self._get_price_list_items(start_year),
        })

    def _get_price_list_items(self, year):
        items = []
        for year in range(self.start_date.year, self.end_date.year + 1):
            item = {
                "applied_on": "3_global",
                "date_start": datetime.datetime(year, 1, 1),
                "date_end": datetime.datetime(year, 12, 31),
                "fixed_price": self._get_price(year),
                # "agreement_year": self.consumer_index_base_year.year,

            }
            _logger.error(f"{self.type_of_cost_increase=}")
            if self.type_of_cost_increase == "index":
                item["compute_price"] = "by_index"
            items.append((0,0,item))
        return items

    def _get_price(self,year):
        if self.type_of_cost_increase == 'percent':
            #TODO: This assumes the formulae COST * (1 + INDEX)  ^ YEAR-DIFF
            quota = (1.0 + self.cost_index / 100) ** (year - self.start_date.year)
            price = self.cost_per_recurrance * quota
            return price
        elif self.type_of_cost_increase in ('index','none'):
            #base_price = self.cost_per_recurrance / self.consumer_index_base_year.index
            return self.contract_yearly_cost
        else:
            raise NotImplementedError       

    def _create_product(self):
        product = self.env["product.product"].search([("name", "=", self._get_product_title())])

        if not product:
            _logger.info("Creating product %s", repr(self._get_product_title()))
            product = self.env["product.product"].sudo().create({
                "name": self._get_product_title(),
                })
        _logger.warning(product)
        return product

    def _create_contract_line(self, contract_id):
        product = self._create_product()

        contract_line_id = self.env["contract.line"].sudo().create({
            "product_id": product.id,
            "contract_id": contract_id.id,
            "name": self._get_product_title(),
            "date_start": self.start_date,
            "date_end": self.end_date,
            "recurring_next_date": self.recurring_start_date or self.start_date,
            "recurring_rule_type": self.recurring_rule_type,
            "recurring_interval": self.recurring_interval,
            "automatic_price": True,
        })



    def store_contract_id(self, agreement, contract_id):
        agreement.contract_id = contract_id

    def save_button(self):

        _logger.warning("Save button pressed")


        price_list = self._create_price_list(self.agreement_id)
        contract_id = self._generate_contract(self.agreement_id, price_list)
        self.store_contract_id(self.agreement_id, contract_id)
        contract_line_id = self._create_contract_line(contract_id)

        # This is a bad idea:
        #today = datetime.date.today()
        #while contract_id.recurring_next_date < today:
        #    contract_id.recurring_create_invoice()
