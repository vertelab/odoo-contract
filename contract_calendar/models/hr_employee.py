# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from dateutil.relativedelta import relativedelta
from odoo.modules.registry import Registry
from odoo import models, fields, api, _
import datetime
import logging
import traceback
import sys
_logger = logging.getLogger(__name__)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    def cron_create_time_report_from_calendar(self, project_id, start_from=False):
        # _logger.warning(f"before code {project_id}")
        if start_from == False:
            today = datetime.date.today()
            current_weeks_monday = today + datetime.timedelta(days=-today.weekday())
        else:
            today = datetime.datetime.strptime(start_from, '%Y-%m-%d')
            current_weeks_monday = today + datetime.timedelta(days=-today.weekday())
        for tr in self.create_time_reports(current_weeks_monday):
            tr.timesheet_ids = [(5, 0, 0)]
            # _logger.warning(f"tr: {tr}")
            for attendee in self.env['calendar.attendee'].search([('partner_id', '=', tr.employee_id.user_partner_id.id), 
                                ('event_date_start', '>=', tr.date_start), ('event_date_start', '<=', tr.date_end)]):
                # _logger.warning(f"attendee: {attendee}")
                line = self.env['account.analytic.line'].create({
                        'date': attendee.event_date_start.date(),
                        'project_id': attendee.contract_id.project_id.id,
                        'name': attendee.contract_id.contract_line_fixed_ids[0].name,
                        'unit_amount': attendee.event_id.duration,
                        'sheet_id': tr.id,
                        'employee_id': tr.employee_id.id,
                })
                tr.write({'timesheet_ids': [(4, line.id, 0)]})
                # _logger.warning(f"line: {line.name}")
            
    def create_time_reports(self, current_weeks_monday):
        all_time_reports = self.env['hr_timesheet.sheet']
        # _logger.warning(f" before code method 2{all_time_reports}")
        for employee in self.env['hr.employee'].search([('user_id', '!=', False)]):
            employee_browse = self.env['hr.employee'].browse(employee.id)
            time_reports = self.env['hr_timesheet.sheet'].search([('employee_id', '=', employee.id)])
            # _logger.warning(f"inside method 2, inside for {employee}")
            if len(time_reports) == 0:
                time_sheet = self.env['hr_timesheet.sheet'].create({
                        'employee_id':employee.id,
                        'user_id': employee_browse.user_id.id,
                        'date_start':current_weeks_monday,
                        'date_end':current_weeks_monday + datetime.timedelta(days=7),
                        'state': 'draft',
                        'review_policy': 'hr',
                    })

                time_sheet._compute_line_ids()
                time_sheet._compute_timesheet_ids()
                all_time_reports += time_sheet
                # _logger.warning(f"inside method 2, inside bottom if")
            else:
                # _logger.warning(f"inside method 2, inside else")
                while current_weeks_monday >= time_reports[-1].date_start:
                    time_sheet = self.env['hr_timesheet.sheet'].create({
                            'employee_id':employee.id,
                            'date_start':time_reports[-1].date_start + datetime.timedelta(days=7),
                            'date_end':time_reports[-1].date_end + datetime.timedelta(days=7)
                        })
                    time_sheet._compute_line_ids()
                    time_sheet._compute_timesheet_ids()
                    all_time_reports += time_sheet
        # _logger.warning(f"after code method 2{all_time_reports}")
        return all_time_reports
