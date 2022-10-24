from distutils.util import Mixin2to3
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ExtendAttendee(models.Model):
    _inherit = 'calendar.attendee'

    contract_id = fields.Many2one(comodel_name='contract.contract', related='event_id.contract_id', store=True)
    