from distutils.util import Mixin2to3
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from datetime import date, datetime

import pytz

_logger = logging.getLogger(__name__)

class ExtendAttendee(models.Model):
    _inherit = "calendar.attendee"

    contract_id = fields.Many2one(comodel_name='contract.contract', related='event_id.contract_id', store=True, readonly=False)
    # contract_skill_ids = fields.Many2many(related='contract_id.skill_ids', readonly=False)
    # contract_allergy_ids = fields.Many2many(related='contract_id.allergy_ids', readonly=False)
    state = fields.Selection(readonly=False)
    customer = fields.Many2one(comodel_name='res.partner', related='event_id.contract_id.partner_id')
    
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
        attendees = self.env["calendar.attendee"]
        for vals in vals_list:
            write_state = 'accepted'
            # _logger.warning(f"ATTENDEE CREATE {vals}")
            attendee = super().create(vals)
            # _logger.warning(f' BYPIDI CREATE {self} {vals_list} {attendees}')
            # event = self.env['calendar.event'].browse(vals_list[0]['event_id'])

            partner = self.env['res.partner'].browse(vals['partner_id'])
            try:
                employee_id = partner.user_ids[0].employee_id[0].id
            except IndexError:
                # _logger.warning('hello')
                raise UserError('Attendee must be an employee')

            leave_periods = self.env['hr.leave'].search([('employee_id', '=', employee_id)]).ids

            event = self.env['calendar.event'].browse(vals['event_id'])
            # _logger.warning(f" BOPIDI {self.env['calendar.event'].search_read([('id', '=', vals_list[0]['event_id'])], [])}")q

            for leave_id in leave_periods:
                leave = self.env['hr.leave'].browse(leave_id)
                # try:
                if leave.date_from <= event.stop and event.start <= leave.date_to:
                    attendee.write({'state': 'declined'})
                    write_state = 'declined'
                    break
                else:
                    self.write({'state': 'accepted'})
                # except TypeError:
                #     if leave['request_date_from'] <= (event.start + datetime.timedelta(hours=event.duration)).date() and event.start.date() <= leave['request_date_to']:
                #         attendee.state = "tentative"

            if write_state != 'declined':
                current_tz = pytz.timezone('UTC')
                workdays = partner.user_ids[0].employee_id[0].resource_calendar_id.attendance_ids
                today_int = datetime.today().weekday()

                work_intervals = partner.user_ids[0].employee_id[0].resource_calendar_id[0]._work_intervals(attendee.event_date_start.astimezone(current_tz), 
                                                                                                            attendee.event_date_end.astimezone(current_tz))

                
                if len(work_intervals._items) != 0:
                    acceptable_count = 0
                    for count, interval in enumerate(work_intervals._items[0]):
                        # _logger.warning(count)
                        # _logger.warning(interval)
                        if count == 0:
                            # _logger.warning(f"Timezone shenanigans incoming {self.event_date_start} {interval} {current_tz.localize(self.event_date_start) >= interval} {current_tz.localize(self.event_date_end) <= interval}")
                            if current_tz.localize(attendee.event_date_start) >= interval:
                                acceptable_count += 1
                                # _logger.warning("A")
                                continue

                        if count == 1:
                            # _logger.warning(f"Timezone shenanigans incoming {self.event_date_start} {interval} {current_tz.localize(self.event_date_start) >= interval} {current_tz.localize(self.event_date_end) <= interval}")
                            if current_tz.localize(attendee.event_date_end) <= interval:
                                acceptable_count += 1
                                # _logger.warning("C")
                                continue

                    # _logger.warning(f"{acceptable_count}")
                    if acceptable_count != 0:
                        filtered = list(filter(lambda day: int(day.dayofweek) == int(today_int), workdays))
                        # _logger.warning(self.event_date_start.hour)
                        # _logger.warning(filtered[0].hour_to)
                        # _logger.warning(self.event_date_end.hour)
                        # _logger.warning(filtered[1].hour_from)
                        hour_to_datetime = current_tz.localize(attendee.event_date_start.replace(hour=int(filtered[0].hour_to)))
                        hour_from_datetime = current_tz.localize(attendee.event_date_end.replace(hour=int(filtered[0].hour_from)))
                        # _logger.warning(f"Timezone shenanigans IF {hour_to_datetime} {hour_from_datetime}")
                        if acceptable_count == 2:
                            attendee.write({'state': 'accepted'})
                            write_state = 'accepted'
                        elif acceptable_count == 1:
                            attendee.write({'state': 'tentative'})
                            write_state = 'tentative'
                        # else:
                        #     self.write({'state': 'declined'})
                        #     write_state = 'declined'
                        #     # _logger.warning("E")
                    else:
                        attendee.write({'state': 'declined'})
                        write_state = 'declined'
                else:
                    # _logger.warning(current_tz.localize(self.event_date_start))
                    # filtered = list(filter(lambda day: int(day.dayofweek) == int(today_int), workdays))

                    attendee.write({'state': 'declined'})
                    write_state = 'declined'
                    # _logger.warning(f"F {write_state}")

            attendee_ids = attendee.event_id.attendee_ids
            ID = self.id            
            if not self.env.context.get('dont_write'):
                for attendee_id in attendee_ids:
                    attendee_id.with_context({'dont_write': True}).write({'state': write_state})

            attendees += attendee
        return attendees    