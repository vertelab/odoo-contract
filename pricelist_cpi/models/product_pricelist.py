import logging
import datetime
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class PricelistConsumerPriceIndexItem(models.Model):
    _inherit = "product.pricelist.item"
    _description = "Consumer Price Indexi Item"

    #TODO: If we want to pick what table we want to associate, do that.

    compute_price = fields.Selection(
        selection_add=[('by_index', 'By Index')],
        ondelete={'by_index': 'set default'},
        help="Use the discount rules and activate the discount settings" \
        " in order to show discount to customer.",
        index=True, 
        default='fixed', 
        required=True)

    agreement_year = fields.Integer(
            string="Agreement Year",
            )
    index_year = fields.Integer(
            string="Index Year",
            compute="_compute_index_year"
            )

    def _compute_index_year(self):
        for item in self:
            if item.agreement_year:
                item.index_year = item.date_start.year - 1
            else:
                item.index_year = False

    def _get_year_index(self, year):
        try:
            return self.env["consumer.price.index"].search([('year', '=', year)]).index
        except BaseException as e:
            _logger.warning(e)
        return 0

    def _compute_price(self, product, quantity, uom, date, currency=None):        
        self and self.ensure_one()  # self is at most one record
        product.ensure_one()
        uom.ensure_one()

        if self.compute_price != 'by_index':
            _logger.warning("Uninteresting calculation")
            return super(PricelistConsumerPriceIndexItem, self)._compute_price(
                    product,
                    quantity,
                    uom,
                    date,
                    currency)

        base_price = self.fixed_price
        agreement_index = self._get_year_index(self.agreement_year)
        index = self._get_year_index(self.index_year)

        if index <= agreement_index or (not self.agreement_year and not self.index_year):
            return base_price
        
        index_diff = index - agreement_index
        index_quota = index_diff / agreement_index
        return base_price + (index_quota * base_price) 