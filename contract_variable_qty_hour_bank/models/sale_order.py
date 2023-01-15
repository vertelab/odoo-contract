from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrderModifyContract(models.Model):
    _inherit = "sale.order"
