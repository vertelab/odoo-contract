import logging
import datetime
import datetime
from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class ConsumerPriceIndex(models.Model):
    _name = "consumer.price.index"
    _description = "Consumer Price Index"
    _order = "year"

    # TODO: Initialize with KPI values from table (somewhere) when installing module
    # TODO: Decide if KPI values from october is enough, or we need to implement KPI for other months as well
    # TODO: Do we need some other index than KPI, in that case:
    #       Make several tables containing information about 'KPI' / 'MY NEW INDEX' / and so on.
    #       Then give users posibilities to create tables, name them, and use them when calc. costs.

    year = fields.Integer(
            string="Year",
            default=lambda _: datetime.datetime.now().year,
            )

    index = fields.Float(
            string="Consumer Price Index",
            )

