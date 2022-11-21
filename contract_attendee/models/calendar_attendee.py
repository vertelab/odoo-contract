from distutils.util import Mixin2to3
import logging
from odoo import models, fields, api, _
import datetime
from datetime import date, datetime

_logger = logging.getLogger(__name__)

class ExtendAttendee(models.Model):
    _inherit = "calendar.attendee"

    contract_id = fields.Many2one(comodel_name='contract.contract', related='event_id.contract_id', store=True, readonly=False)
    contract_skill_ids = fields.Many2many(related='contract_id.skill_ids', readonly=False)
    contract_allergy_ids = fields.Many2many(related='contract_id.allergy_ids', readonly=False)
    state = fields.Selection(readonly=False)
    
    # @api.depends('event_date_start')
    # def _check_if_during_contract(self):
    #     for rec in self:
    #         if not (isinstance(rec.contract_id.date_end, date) or isinstance(rec.contract_id.date_start, date)):
    #             _logger.warning(f"date_end is bool")
    #             break
        
    #         if rec.event_date_start.date() <= rec.contract_id.date_end and rec.contract_id.date_start <= rec.event_date_end.date():
    #             rec.state = 'accepted'
    #         else:
    #             rec.state = 'declined'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            attendees = super().create(vals)
            # _logger.warning(f' BYPIDI CREATE {self} {vals_list} {attendees}')
            # event = self.env['calendar.event'].browse(vals_list[0]['event_id'])

            partner = self.env['res.partner'].browse(vals['partner_id'])
            employee_id = partner.user_ids[0].employee_id[0].id

            leave_periods = self.env['hr.leave'].search([('employee_id', '=', employee_id)]).ids

            event = self.env['calendar.event'].browse(vals['event_id'])
            # _logger.warning(f" BOPIDI {self.env['calendar.event'].search_read([('id', '=', vals_list[0]['event_id'])], [])}")q

            for leave_id in leave_periods:
                leave = self.env['hr.leave'].browse(leave_id)
                # try:
                if leave.date_from <= event.stop and event.start <= leave.date_to:
                    attendees.write({'state': 'declined'})
                # except TypeError:
                #     if leave['request_date_from'] <= (event.start + datetime.timedelta(hours=event.duration)).date() and event.start.date() <= leave['request_date_to']:
                #         attendee.state = "tentative"

            return attendees    