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

    def _get_year_index(self, year):
        try:
            return self.env["consumer.price.index"].search([('year', '=', year)]).index
        except BaseException as e:
            _logger.warning(e)
        return 0

