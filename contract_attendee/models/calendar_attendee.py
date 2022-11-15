from distutils.util import Mixin2to3
import logging
from odoo import models, fields, api, _
import datetime

_logger = logging.getLogger(__name__)

class ExtendAttendee(models.Model):
    _inherit = "calendar.attendee"

    contract_id = fields.Many2one(comodel_name='contract.contract', related='event_id.contract_id', store=True, readonly=False)
    contract_skill_ids = fields.Many2many(related='contract_id.skill_ids', readonly=False)
    contract_allergy_ids = fields.Many2many(related='contract_id.allergy_ids', readonly=False)
    
    @api.model_create_multi
    def create(self, vals_list):
        attendees = super().create(vals_list)
        _logger.warning(f"BIPIDI {self} {vals_list}")
        # for attendee in attendees:
        #     partner = self.env['res.partner'].browse(vals_list[0]['partner_id'])
        #     user = partner.user_ids[0]
        #     test = user.employee_id[0].leaves
        #     _logger.warning(test)

        #     leave_periods = self.env['hr.leave'].search_read([('user_id', '=', user.id)],[])

        #     event = self.env['calendar.event'].browse(vals_list[0]['event_id'])
        #     # _logger.warning(f" BOPIDI {self.env['calendar.event'].search_read([('id', '=', vals_list[0]['event_id'])], [])}")

        #     for leave in leave_periods:
        #         try:
        #             if leave['request_date_from'] <= event.stop_date and event.start_date <= leave['request_date_to']:
        #                 attendee.state = "tentative"
        #         except TypeError:
        #             if leave['request_date_from'] <= (event.start + datetime.timedelta(hours=event.duration)).date() and event.start.date() <= leave['request_date_to']:
        #                 attendee.state = "tentative"

        return attendees    

    def write(self, vals):
        res = super().write(vals)
        _logger.warning(f"BYPIDI {self} {vals}")
        return res