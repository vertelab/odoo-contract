from distutils.util import Mixin2to3
import logging
from odoo import models, fields, api, _
from datetime import datetime

_logger = logging.getLogger(__name__)

class ExtendAttendee(models.Model):
    _inherit = 'calendar.attendee'

    contract_id = fields.Many2one(comodel_name='contract.contract', related='event_id.contract_id', store=True, readonly=False)
    
    @api.model_create_multi
    def create(self, vals_list):
        attendees = super().create(vals_list)
        for attendee in attendees:
            # _logger.warning(vals_list)
            partner = self.env['res.partner'].browse(vals_list[0]['partner_id'])
            # _logger.warning(partner)
            user = partner.user_ids[0]
            # _logger.warning(user)
            leave_periods = self.env['hr.leave'].search_read([('user_id', '=', user.id)],[])
            # _logger.warning(leave_periods)
            # _logger.warning(user)
            # employee = user.employee_id[0]
            # _logger.warning(employee)
            # off_date_start = employee.leave_date_from
            # off_date_end = employee.leave_date_to
            event = self.env['calendar.event'].browse(vals_list[0]['event_id'])

            # _logger.warning(event)
            # _logger.warning(f"{off_date_start} {off_date_end}")
            # _logger.warning(f"{event_date_start} {event_date_end}")

            # _logger.warning(leave_periods)
            for leave in leave_periods:
                # _logger.warning(f"{leave['request_date_from']}     {leave['request_date_to']}")
                # _logger.warning(f"{event.start_date}     {event.stop_date}")
                if leave['request_date_from'] <= event.stop_date and event.start_date <= leave['request_date_to']:
                    attendee.state = "tentative"

        return attendees    
