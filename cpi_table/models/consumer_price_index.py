import logging
import datetime
import datetime
from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class ConsumerPriceIndex(models.Model):
    _name = "consumer.price.index"
    _description = "Consumer Price Index"
    _order = "year"
    _rec_name = "year"
    # TODO: Initialize with KPI values from table (somewhere) when installing module
    # TODO: Decide if KPI values from october is enough, or we need to implement KPI for other months as well
    # TODO: Do we need some other index than KPI, in that case:
    #       Make several tables containing information about 'KPI' / 'MY NEW INDEX' / and so on.
    #       Then give users posibilities to create tables, name them, and use them when calc. costs.
    # TODO: Stop users from creating duplicate values for year (or at least unique for months?)

    year = fields.Integer(
            string="Year",
            default=lambda _: datetime.datetime.now().year,
            )

    index = fields.Float(
            string="Consumer Price Index",
            )

    is_negative = fields.Boolean(
            string="True if index is negative",
            compute="_is_negative",
            )

    @api.depends("index")
    def _is_negative(self):
        for record in self:
            record.is_negative = record.index < 0 if record.index is not False else True

