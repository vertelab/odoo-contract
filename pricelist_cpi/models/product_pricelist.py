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

    year = fields.Integer(
            string="Year",
            )

    def _get_multiplier_for_year(self, year):
        try:
            return self.env["consumer.price.index"].search([('year', '=', year)]).index
        except BaseException as e:
            _logger.warning(e)
        return 0

    def _compute_price(self, product, quantity, uom, date, currency=None):
        _logger.warning("Computing price")
        if self.compute_price != 'by_index':
            _logger.warning("Uninteresting calculation")
            return super(PricelistConsumerPriceIndexItem, self)._compute_price(
                    product,
                    quantity,
                    uom,
                    date,
                    currency)
        self.ensure_one()
        base_price = self.fixed_price
        price = (product.uom_id._compute_price(base_price, uom) *
                 self._get_multiplier_for_year(self.date_start.year))
        _logger.warning(f"Got the {price=} from {base_price=}, {uom=} {self._get_multiplier_for_year(self.date_start.year)=}")
        return price




