import logging
import datetime
import datetime
from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class PricelistConsumerPriceIndexItem(models.Model):
    _inherit = "product.pricelist.item"
    _description = "Consumer Price Indexi Item"

    #TODO: If we want to pick what table we want to associate, do that.

#    compute_price = fields.Selection(selection_add=[
#        ('by_index', 'By Index'), #TODO: does this need to be _('By index')?
#        ],
#        )

    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('percentage', 'Percentage (discount)'),
        ('formula', 'Formula'),
        ('by_index', 'By Index'),
        ], index=True, default='fixed', required=True)


    year = fields.Many2one(
            "consumer.price.index",
            string="Year",
            )

    def _get_multiplier_for_year(self, year):
        try:
            #row = self.env["consumer.price.index"].search([('year', '=', year)])
            #if len(row) > 1:
            #   _logger.warning(f"Too many rows for {year=}")
            return self.year.index
        except BaseException as e:
            _logger.warning(e)
        return 0

    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        if self.compute_price != 'by_index':
            return super(PricelistConsumerPriceIndexItem, self)._compute_price(
                    price,
                    price_uom,
                    product,
                    quantity,
                    partner)
        self.ensure_one()
        price = (product.uom_id._compute_price(price, price_uom) *
                 self.get_multiplier_for_year(self.date_start.year))




