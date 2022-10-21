import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ExtendAttendee(models.Model):
    _description = "Extend attendee"
    _inherit = 'calendar.attendee'

    m2o_contract = fields.Many2one('contract.contract', string='Contract')