import logging
import datetime
import datetime
from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class PricelistConsumerPriceIndexItem(models.Model):
    _inherit = "product.pricelist.item"
    _description = "Consumer Price Indexi Item"

    #TODO: If we want to pick what table we want to associate, do that.

    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('percentage', 'Percentage (discount)'),
        ('formula', 'Formula'),
        ('by_index', 'By Index'),
        ], index=True, default='fixed', required=True)


#    year = fields.Many2one(
#            "consumer.price.index",
    year = fields.Integer(
            string="Year",
            )

    def _get_multiplier_for_year(self, year):
        try:
            return self.env["consumer.price.index"].search([('year', '=', year)]).index
        except BaseException as e:
            _logger.warning(e)
        return 0

    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        _logger.warning("Computing price")
        if self.compute_price != 'by_index':
            _logger.warning("Uninteresting calculation")
            return super(PricelistConsumerPriceIndexItem, self)._compute_price(
                    price,
                    price_uom,
                    product,
                    quantity,
                    partner)
        self.ensure_one()
        price = (product.uom_id._compute_price(price, price_uom) *
                 self._get_multiplier_for_year(self.date_start.year))
        _logger.warning(f"Got the {price=}")
        _logger.warning(f"{dir(self)}")
        return price




