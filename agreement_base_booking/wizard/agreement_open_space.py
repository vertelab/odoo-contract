from odoo import models, fields, api, _
from datetime import datetime, timedelta

class AgreementOpenSpace(models.TransientModel):
    _name = 'agreement.open.space'
    _description = 'Agreement Open Space'

    @api.model
    def _default_start(self):
        now = fields.Datetime.now()
        return now + (datetime.min - now) % timedelta(minutes=30)

    @api.model
    def _default_stop(self):
        now = fields.Datetime.now()
        start = now + (datetime.min - now) % timedelta(minutes=30)
        return start + timedelta(days=30)

    agreement_id = fields.Many2one('agreement', string="Agreement")


    @api.model
    def _default_start(self):
        # Din befintliga _default_start() logik här, eller:
        return fields.Date.context_today(self)

    @api.model
    def _default_stop(self):
        return fields.Date.context_today(self) + timedelta(days=30)

    start_date = fields.Date(string="Start Date", default='_default_start', required=True)
    end_date = fields.Date(string="End Date", default='_default_stop', required=True)


    mon = fields.Boolean(readonly=False)
    tue = fields.Boolean(readonly=False)
    wed = fields.Boolean(readonly=False)
    thu = fields.Boolean(readonly=False)
    fri = fields.Boolean(readonly=False)
    sat = fields.Boolean(readonly=False)
    sun = fields.Boolean(readonly=False)

    def action_open_resource(self):
        resource_id = self.agreement_id.second_hand_booking_resource_id
        if not resource_id:
            return

        attendance_vals = []

        # Map boolean fields to dayofweek values
        day_mapping = [
            (self.mon, '0', 'Monday'),
            (self.tue, '1', 'Tuesday'),
            (self.wed, '2', 'Wednesday'),
            (self.thu, '3', 'Thursday'),
            (self.fri, '4', 'Friday'),
            (self.sat, '5', 'Saturday'),
            (self.sun, '6', 'Sunday'),
        ]

        # Create attendance records only for selected days
        for is_selected, dayofweek, day_name in day_mapping:
            if is_selected:
                attendance_vals.append((0, 0, {
                    'name': f'{day_name} [{self.start_date} - {self.end_date}]',
                    'dayofweek': dayofweek,
                    'day_period': 'morning',
                    'hour_from': 0.0,  # 00:00
                    'hour_to': 24.0,  # 24:00
                    'date_from': self.start_date,
                    'date_to': self.end_date
                }))

        # Update the resource calendar with new attendance records
        if attendance_vals:
            resource_id.resource_calendar_id.attendance_ids = attendance_vals

        return {'type': 'ir.actions.act_window_close'}

