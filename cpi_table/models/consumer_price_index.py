import logging
import datetime

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


#class ConsumerPriceTable(models.Model):
#    _name = "consumer.price"
#    _description = "consumer price index - table"

#    rows = fields.One2many(
#            "consumer.price.index",
#            "table",
#            string="Rows",
#            )

class ConsumerPriceIndex(models.Model):
    _name = "consumer.price.index"
    _description = "Consumer Price Index"
    _order = "year"

    year = fields.Integer(
            string="Year",
            )

    index = fields.Float(
            string="Consumer Price Index",
            )

#    table = fields.Many2one(
#            "consumer.price",
#            string="Table",
#            )

