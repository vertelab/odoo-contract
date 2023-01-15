import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"
  
#TODO: if there is a contract in the making and a line with this product then update ????

